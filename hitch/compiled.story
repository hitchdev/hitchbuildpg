Built App:
  based on: base postgres
  description: |
    Build postgres.
  given:
    postgres_version: 10.3
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp(postgres_version).with_build_path(".")
  steps:
  - Run: |
      pgapp.ensure_built()
      assert postgres_version in pgapp.bin.postgres("--version").output(), \
        "--version returned {0}".format(pgapp.bin.postgres("--version").output())

        
Created Database and User:
  based on: base postgres
  given:
    postgres_version: 10.3
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp(postgres_version).with_build_path(share)

      pgdata = hitchbuildpg.PostgresDatafiles("myappdata", pgapp).with_build_path(".")
      pguser = hitchbuildpg.PostgresUser(pgdata, "myuser", "mypassword").with_build_path(".")
      pgdatabase = hitchbuildpg.PostgresDatabase(pgdata, pguser, "mydb").with_build_path(".")
  steps:
  - Run: |
      pgdatabase.ensure_built()
      
