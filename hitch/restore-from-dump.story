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

      pgdata = hitchbuildpg.PostgresDatafiles("myappdata", pgapp)
      pguser = hitchbuildpg.PostgresUser(pgdata, "myuser", "mypassword")
      pgdatabase = hitchbuildpg.PostgresDatabase(
          pgdata, pguser, "mydb"
      ).from_dump("dump.sql").with_build_path(".")
  steps:
  - Run: |
      pgdatabase.ensure_built()
      
      running_db = pgdatabase.postgres.pexpect()
      running_db.expect("database system is ready")
      
      assert "London" in pgdatabase.psql("-c", "select name from cities where location = 'GB';").output()
      
      import os
      import signal
      os.kill(running_db.pid, signal.SIGTERM)
      running_db.close()
