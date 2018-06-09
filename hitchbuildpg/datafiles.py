from commandlib import CommandPath, Command
from distutils.version import LooseVersion
from hitchbuildpg import utils
from path import Path
import hitchbuild
import pexpect
import signal
import os


class PostgresServer(object):
    def __init__(self, datafiles):
        self._datafiles = datafiles

    def start(self):
        self._pexpect = self._datafiles.postgres("-p", "15432").pexpect()
        self._pexpect.expect("database system is ready")

    @property
    def psql(self):
        return self._datafiles.psql("-p", "15432")

    def stop(self):
        os.kill(self._pexpect.pid, signal.SIGTERM)
        self._pexpect.expect(pexpect.EOF)
        self._pexpect.close()


class DataBuild(object):
    def from_datafiles(self, datafiles):
        self._datafiles = datafiles
        return self

    def build(self):
        self._server = self._datafiles.server()
        self._server.start()
        self.run()
        self._server.stop()

    def run_sql_as_root(self, sql):
        return self._server.psql("-d", "template1", "-c", sql).run()

    @property
    def psql(self):
        return self._server.psql

    def load_database_dump(self, database, username, password, filename):
        self._server.psql(
            "-U", username, "-p", "15432", "-d", database, "-f", str(filename)
        ).with_env(PG_PASSWORD=password).run()


class PostgresDatafiles(hitchbuild.HitchBuild):
    def __init__(self, name, postgresapp, databuild):
        self._name = name
        self._databuild = databuild
        self.postgresapp = self.as_dependency(postgresapp)

    def fingerprint(self):
        return (self._name,)

    @property
    def basepath(self):
        return self.build_path.joinpath(self.name).abspath()

    @property
    def workingpath(self):
        return self.basepath / "working"

    @property
    def snapshotpath(self):
        return self.basepath / "snapshot"

    @property
    def postgres(self):
        return self.postgresapp.bin.postgres.with_trailing_args(
            "-D",
            self.workingpath,
            "--unix_socket_directories={0}".format(self.workingpath),
            "--log_destination=stderr",
        )

    @property
    def psql(self):
        return self.postgresapp.bin.psql("--host", self.workingpath)

    def server(self):
        return PostgresServer(self)

    def build(self):
        if not self.basepath.exists():
            self.basepath.mkdir()
            self.workingpath.mkdir()
            self.snapshotpath.mkdir()
            self.postgresapp.bin.initdb(self.workingpath).run()
            self._databuild.from_datafiles(self).build()
            Command("rsync")(
                "--del",
                "-av",
                # Trailing slash so contents are moved not whole dir
                self.workingpath + "/",
                self.snapshotpath,
            ).run()
        else:
            Command("rsync")(
                "--del", "-av", self.snapshotpath + "/", self.workingpath
            ).run()

    def clean(self):
        if self.basepath.exists():
            self.basepath.rmtree()
