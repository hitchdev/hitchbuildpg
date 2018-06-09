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

    def kill(self):
        os.kill(self._pexpect.pid, signal.SIGQUIT)
        self._pexpect.expect(pexpect.EOF)
        self._pexpect.close()
