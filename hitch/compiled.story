Postgres App:
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
