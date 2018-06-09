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
