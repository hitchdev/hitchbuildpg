Created Database and User:
  based on: base postgres
  given:
    postgres_version: 10.3
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp(postgres_version).with_build_path(share)

      pgdata = hitchbuildpg.PostgresDatafiles("myappdata", pgapp)
      pguser = hitchbuildpg.PostgresUser(pgdata, "myuser", "mypassword")
      pgdatabase = hitchbuildpg.PostgresDatabase(pgdata, pguser, "mydb").with_build_path(".")
  steps:
  - Run: |
      pgdatabase.ensure_built()
