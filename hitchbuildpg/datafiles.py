from commandlib import CommandPath, Command
from distutils.version import LooseVersion
from hitchbuildpg import utils
from path import Path
import hitchbuild



class PostgresDatafiles(hitchbuild.HitchBuild):
    def __init__(self, name, postgresapp):
        self._name = name
        self.postgresapp = self.as_dependency(postgresapp)

    def fingerprint(self):
        return (self._name,)

    @property
    def basepath(self):
        return self.build_path.joinpath(self.name)
    
    @property
    def postgres(self):
        return self.postgresapp.bin.postgres.with_trailing_args(
            "-D", self.basepath,
            "--unix_socket_directories={0}".format(self.basepath),
            "--log_destination=stderr",
        )
    
    @property
    def psql(self):
        return self.postgresapp.bin.psql

    def build(self):
        if not self.basepath.exists():
            self.basepath.mkdir()
            self.postgresapp.bin.initdb(self.basepath).run()

    def clean(self):
        if self.basepath.exists():
            self.basepath.rmtree()
