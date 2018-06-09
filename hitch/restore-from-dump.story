Working on restorable database dump:
  based on: base postgres
  about: |
    Using hitchbuildpg you can build database files from a normal
    SQL dump, work on it, change it and then wipe and rebuild again
    from a snapshot taken after the first build.
  given:
    postgres_version: 10.3
    files:
      dump.sql: |
        CREATE TABLE cities (
            name            varchar(80),
            location        varchar(80)
        );

        INSERT INTO cities values ('London', 'GB');
        INSERT INTO cities values ('Paris', 'France');
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp(postgres_version).with_build_path(share)
      
      class DataBuild(hitchbuildpg.DataBuild):
          def run(self):
              self.run_sql_as_root("create user myuser with password 'mypassword';")
              self.run_sql_as_root("create database mydb with owner myuser;")
              self.load_database_dump(
                  database="mydb",
                  username="myuser",
                  password="mypassword",
                  filename="dump.sql"
              )

      pgdata = hitchbuildpg.PostgresDatafiles(
          "myappdata",
          pgapp,
          DataBuild(),
      ).with_build_path(".")
  steps:
  - Run: |
      pgdata.ensure_built()
      
      db_service = pgdata.server()
      db_service.start()
      
      psql = db_service.psql(
          "-U", "myuser", "-p", "15432", "-d", "mydb",
      ).with_env(PG_PASSWORD="mypassword")
      
      assert "London" in psql(
          "-c", "select name from cities where location = 'GB';"
      ).output()
      
      psql("-c", "delete from cities where location = 'GB';").run()
      
      import time
      time.sleep(0.2)
      
      db_service.stop()
  - Run: |
      # This will restore the data to its original state
      pgdata.ensure_built()
      
      db_service = pgdata.server()
      db_service.start()
      
      psql = db_service.psql(
          "-U", "myuser", "-p", "15432", "-d", "mydb",
      ).with_env(PG_PASSWORD="mypassword")
      
      print(psql("-c", "select name from cities where location = 'GB';").output())
      
      assert "London" in psql("-c", "select name from cities where location = 'GB';").output()
      
      db_service.stop()
