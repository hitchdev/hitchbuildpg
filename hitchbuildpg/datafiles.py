from hitchbuildpg.server import PostgresServer
from commandlib import Command
from path import Path
import hitchbuild


class PostgresDatafiles(hitchbuild.HitchBuild):
    def __init__(self, build_path, postgresapp, databuild):
        self.buildpath = Path(build_path).abspath()
        self._databuild = databuild
        self.fingerprint_path = self.buildpath / "fingerprint.txt"
        self.postgresapp = self.dependency(postgresapp)

    @property
    def workingpath(self):
        return self.buildpath / "working"

    @property
    def snapshotpath(self):
        return self.buildpath / "snapshot"

    @property
    def postgres(self):
        return self.postgresapp.build.bin.postgres.with_trailing_args(
            "-D",
            self.workingpath,
            "--unix_socket_directories={0}".format(self.workingpath),
            "--log_destination=stderr",
        )

    @property
    def psql(self):
        return self.postgresapp.build.bin.psql("--host", self.workingpath)

    def server(self):
        return PostgresServer(self)

    def build(self):
        if self.incomplete() or self.postgresapp.rebuilt:
            self.postgresapp.build.ensure_built()
            self.buildpath.rmtree(ignore_errors=True)
            self.buildpath.mkdir()
            self.workingpath.mkdir()
            self.snapshotpath.mkdir()
            self.postgresapp.build.bin.initdb(self.workingpath).run()
            self._databuild.from_datafiles(self).build()
            self._rsync(self.workingpath, self.snapshotpath)
            self.refingerprint()
        else:
            self._rsync(self.snapshotpath, self.workingpath)

    def _rsync(self, from_path, to_path):
        Command("rsync")(
            "--del",
            "-av",
            # Trailing slash so contents are moved not whole dir
            from_path + "/",
            to_path,
        ).run()

    def clean(self):
        if self.buildpath.exists():
            self.buildpath.rmtree()
