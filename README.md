# HitchBuildPg

A small, self contained python library for building postgres database locally that, on first run will:

* Downloads and compiles a specified version of postgres.

* Builds a database from a series of SQL commands and by restoring a database dump file.

* Takes a snapshot of the newly built database files by taking a copy of the folder.

On subsequent builds, it will skip the long, expensive steps of downloading, compiling postgres
and restoring a database from a .sql file and just overwrite the data files.


```python
import hitchbuildpg

postgres_version = "10.10"
    
pgapp_dir = "{}/postgres-{}".format(share, postgres_version)

pgapp = hitchbuildpg.PostgresApp(pgapp_dir, postgres_version)

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
    "./myappdata",
    pgapp,
    DataBuild(),
)

pgdata.ensure_built()

db_service = pgdata.server()
db_service.start()

psql = db_service.psql(
    "-U", "myuser", "-p", "15432", "-d", "mydb",
).with_env(PG_PASSWORD="mypassword")

psql("-c", "select name from cities where location = 'GB';").run()

# Prints output of SQL statement
    
psql("-c", "delete from cities where location = 'GB';").run()
      
db_service.stop()
```

