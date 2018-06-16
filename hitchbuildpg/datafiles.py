from hitchbuildpg.server import PostgresServer
from commandlib import Command
import hitchbuild


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
        if not self.basepath.exists() or self.last_run_had_exception:
            self.basepath.rmtree(ignore_errors=True)
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
