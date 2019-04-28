from commandlib import CommandPath, Command
from hitchbuildpg import utils
import hitchbuild


class PostgresApp(hitchbuild.HitchBuild):
    def __init__(self, version):
        self.version = version

    @property
    def basepath(self):
        return self.build_path.joinpath("postgres{0}".format(self.version))

    @property
    def bin(self):
        return CommandPath(self.full_directory / "bin")

    def fingerprint(self):
        return str(hash(self.version))

    def clean(self):
        self.basepath.rmtree(ignore_errors=True)

    @property
    def full_directory(self):
        return self.basepath.joinpath("postgresql-{}".format(self.version))

    def build(self):
        if not self.basepath.exists() or self.last_run_had_exception:
            self.basepath.rmtree(ignore_errors=True)
            self.basepath.mkdir()

            download_to = self.basepath.joinpath(
                "postgresql-{}.tar.gz".format(self.version)
            )
            utils.download_file(
                download_to,
                "https://ftp.postgresql.org/pub/source/v{0}/postgresql-{0}.tar.gz".format(
                    self.version
                ),
            )
            utils.extract_archive(download_to, self.basepath)

            print("Running ./configure --with-openssl --prefix={}".format(self.full_directory))
            Command("./configure")("--prefix={}".format(self.full_directory)).in_dir(
                self.full_directory
            ).run()
            print("Running make world")
            Command("make", "world").in_dir(self.full_directory).run()
            print("Running make install")
            Command("make")("install").in_dir(self.full_directory).run()
            print("Running make install for contrib")
            Command("make")("install").in_dir(self.full_directory / "contrib").run()
        self.verify()

    def verify(self):
        version_to_check = self.version.replace("-dev", "")
        assert (
            version_to_check in self.bin.postgres("--version").output()
        ), "'{0}' expected to be found in postgres --version, got:\n{1}".format(
            self.version, self.bin.postgres("--version").output()
        )
