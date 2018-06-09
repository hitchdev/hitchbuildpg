from commandlib import CommandPath, Command
from distutils.version import LooseVersion
from hitchbuildpg import utils
from path import Path
from copy import copy
import hitchbuild
import signal
import os


class PostgresServer(object):
    def __init__(self, db_build):
        self._db_build = db_build

    def start(self):
        self._pexpect = self._db_build.datafiles.postgres("-p", "15432").pexpect()
        self._pexpect.expect("database system is ready")

    def stop(self):
        os.kill(self._pexpect.pid, signal.SIGTERM)
        self._pexpect.close()


class PostgresDatabase(hitchbuild.HitchBuild):
    def __init__(self, datafiles, owner, name):
        self.datafiles = self.as_dependency(datafiles)
        self.owner = self.as_dependency(owner)
        self._name = name
        self._dump_filename = None

    def fingerprint(self):
        return (self._name,)

    def from_dump(self, filename):
        new_pgdb = copy(self)
        new_pgdb._dump_filename = filename
        return new_pgdb

    @property
    def psql(self):
        return self.datafiles.psql(
            "-U",
            self.owner.name,
            "-d",
            self._name,
            "-p",
            "15432",
            "--host",
            self.datafiles.basepath,
        ).with_env(PG_PASSWORD=self.owner.password)

    def server(self):
        return PostgresServer(self)

    def build(self):
        server = self.server()
        server.start()

        print("Creating user")
        psql_superuser = self.datafiles.psql(
            "-d", "template1", "-p", "15432", "--host", self.datafiles.basepath
        )

        print("Creating database")
        psql_superuser(
            "-c", "create database {} with owner {};".format(self.name, self.owner.name)
        ).run()

        if self._dump_filename is not None:
            print("Restoring database from dump...")
            self.psql("-f", self._dump_filename).run()

        server.stop()
