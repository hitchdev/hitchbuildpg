HitchBuildPg
============

A small, self contained python library for building postgres database locally that, on first run will:

* Downloads and compiles a specified version of postgres.

* Builds a database from a series of SQL commands and by restoring a database dump file.

* Takes a snapshot of the newly built database files by taking a copy of the folder.

On subsequent builds, it will skip the long, expensive steps of downloading, compiling postgres
and restoring a database from a .sql file and just rsync the files across.
