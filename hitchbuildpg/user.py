from commandlib import CommandPath, Command
from distutils.version import LooseVersion
from hitchbuildpg import utils
from path import Path
import hitchbuild
import signal
import os


class PostgresUser(hitchbuild.HitchBuild):
    def __init__(self, datafiles, name, password):
        self.datafiles = self.as_dependency(datafiles)
        self._name = name
        self.password = password

    def fingerprint(self):
        return (self._name, self.password)

    def build(self):
        server = self.datafiles.postgres("-p", "15432").pexpect()
        server.expect("database system is ready")
        psql = self.datafiles.psql(
            "-d", "template1", "-p", "15432", "--host", self.datafiles.basepath
        )
        psql(
            "-c", "create user {} with password '{}';".format(self.name, self.password)
        ).run()

        os.kill(server.pid, signal.SIGTERM)
        server.close()
