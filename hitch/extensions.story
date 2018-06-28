Extensions:
  based on: base postgres
  about: |
    By default, Postgres extensions are compiled in on hitchbuildpg,
    but you need to do 'create extension' to use them.

    Full list of extensions:

    https://www.postgresql.org/docs/9.5/static/contrib.html
  given:
    postgres_version: 10.3
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp(postgres_version).with_build_path(share)

      class DataBuild(hitchbuildpg.DataBuild):
          def run(self):
              self.run_sql_as_root("create extension fuzzystrmatch;")
              self.run_sql_as_root("create user myuser with password 'mypassword';")
              self.run_sql_as_root("create database mydb with owner myuser;")

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

      # Using "dmetaphone" to get double metaphones
      # from fuzzystrmatch extension
      assert "KMP" in psql(
          "-c", "select dmetaphone('gumbo');"
      ).output()

      import time
      time.sleep(0.2)

      db_service.stop()
