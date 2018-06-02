from commandlib import CommandPath, Command
from distutils.version import LooseVersion
from hitchbuildpg import utils
from path import Path
import hitchbuild
import signal
import os


class PostgresDatabase(hitchbuild.HitchBuild):
    def __init__(self, datafiles, owner, name):
        self.datafiles = self.as_dependency(datafiles)
        self.owner = self.as_dependency(owner)
        self._name = name
    
    def fingerprint(self):
        return (self._name,)

    def build(self):
        server = self.datafiles.postgres("-p", "15432").pexpect()
        server.expect("database system is ready")
        psql = self.datafiles.psql(
            "-d", "template1", "-p", "15432", "--host", self.datafiles.basepath,
        )
        psql(
            "-c",
            "create database {} with owner {};".format(
                self.name,
                self.owner.name,
            )
        ).run()
        
        os.kill(server.pid, signal.SIGTERM)
        server.close()
        
