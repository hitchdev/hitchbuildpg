Restored database dump:
  based on: base postgres
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
              self.create_user("myuser", "mypassword")
              self.create_db("mydb", "myuser")
              self.restore_from_dump(
                  "mydb", "myuser", "mypassword", "dump.sql"
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
      
      db_service.stop()
  - Run: |
      # This will snap the datafiles back to 
      pgdata.ensure_built()
      
      db_service = pgdata.server()
      db_service.start()
      
      psql = db_service.psql(
          "-U", "myuser", "-p", "15432", "-d", "mydb",
      ).with_env(PG_PASSWORD="mypassword")
      
      assert "London" in psql("-c", "select name from cities where location = 'GB';").output()
      
      db_service.stop()
