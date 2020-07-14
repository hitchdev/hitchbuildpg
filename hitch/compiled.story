Built App:
  based on: base postgres
  about: |
    Build postgres.
  given:
    postgres_version: 10.3
    setup: |
      import hitchbuildpg

      pgapp = hitchbuildpg.PostgresApp("./postgres", postgres_version)
  steps:
  - Run: |
      pgapp.ensure_built()
      assert postgres_version in pgapp.bin.postgres("--version").output(), \
        "--version returned {0}".format(pgapp.bin.postgres("--version").output())
      

