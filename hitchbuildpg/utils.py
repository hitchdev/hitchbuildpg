from commandlib import Command, CommandError
import patoolib
import shutil
import os


def log(message):
    print(message)


def extract_archive(filename, directory):
    patoolib.extract_archive(filename, outdir=directory)


class DownloadError(Exception):
    pass


def download_file(downloaded_file_name, url, max_connections=2, max_concurrent=5):
    """Download file to specified location."""
    if os.path.exists(downloaded_file_name):
        return

    log("Downloading: {}\n".format(url))
    aria2c = Command("aria2c")
    aria2c = aria2c("--max-connection-per-server={}".format(max_connections))
    aria2c = aria2c("--max-concurrent-downloads={}".format(max_concurrent))

    try:
        if os.path.isabs(downloaded_file_name):
            aria2c("--dir=/", "--out={}.part".format(downloaded_file_name), url).run()
        else:
            aria2c("--dir=.", "--out={}.part".format(downloaded_file_name), url).run()
    except CommandError:
        raise DownloadError(
            "Failed to download {}. Re-running may fix the problem.".format(url)
        )

    shutil.move(downloaded_file_name + ".part", downloaded_file_name)
