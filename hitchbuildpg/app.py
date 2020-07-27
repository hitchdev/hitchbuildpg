from commandlib import CommandPath, Command
from hitchbuildpg import utils
from path import Path
import hitchbuild
import shutil


class PostgresApp(hitchbuild.HitchBuild):
    def __init__(self, build_path, version):
        self.buildpath = Path(build_path).abspath()
        self.fingerprint_path = self.buildpath / "fingerprint.txt"
        self.version = version

    @property
    def bin(self):
        return CommandPath(self.buildpath / "bin")

    def clean(self):
        self.buildpath.rmtree(ignore_errors=True)

    def build(self):
        if self.incomplete():
            self.buildpath.rmtree(ignore_errors=True)
            self.buildpath.mkdir()

            download_to = self.tmp / "postgresql-{}.tar.gz".format(self.version)
            utils.download_file(
                download_to,
                "https://ftp.postgresql.org/pub/source/v{0}/postgresql-{0}.tar.gz".format(
                    self.version
                ),
            )
            utils.extract_archive(download_to, self.buildpath)
            download_to.remove()

            for filepath in self.buildpath.joinpath(
                "postgresql-{}".format(self.version)
            ).listdir():
                shutil.move(filepath, self.buildpath)
            self.buildpath.joinpath("postgresql-{}".format(self.version)).rmdir()

            print(
                "Running ./configure --with-openssl --prefix={}".format(self.buildpath)
            )
            Command("./configure")("--with-openssl", "--prefix={}".format(self.buildpath)).in_dir(
                self.buildpath
            ).run()
            print("Running make world")
            Command("make", "world").in_dir(self.buildpath).run()
            print("Running make install")
            Command("make")("install").in_dir(self.buildpath).run()
            print("Running make install for contrib")
            Command("make")("install").in_dir(self.buildpath / "contrib").run()
            self.verify()
            self.refingerprint()

    def verify(self):
        version_to_check = self.version.replace("-dev", "")
        assert (
            version_to_check in self.bin.postgres("--version").output()
        ), "'{0}' expected to be found in postgres --version, got:\n{1}".format(
            self.version, self.bin.postgres("--version").output()
        )
