import random
import string
import shutil
import os


class DownloadError(Exception):
    pass


def download_file(downloaded_file_name, url, max_connections=2, max_concurrent=5):
    """Download file to specified location."""
    from commandlib import Command, CommandError, run
    if os.path.exists(downloaded_file_name):
        return

    print("Downloading: {}\n".format(url))
    aria2c = Command("aria2c")
    aria2c = aria2c("--max-connection-per-server={}".format(max_connections))
    aria2c = aria2c("--max-concurrent-downloads={}".format(max_concurrent))

    try:
        if os.path.isabs(downloaded_file_name):
            run(aria2c("--dir=/", "--out={}.part".format(downloaded_file_name), url))
        else:
            run(aria2c("--dir=.", "--out={}.part".format(downloaded_file_name), url))
    except CommandError:
        raise DownloadError("Failed to download {}. Re-running may fix the problem.".format(url))

    shutil.move(downloaded_file_name + ".part", downloaded_file_name)


def random_id(length):
    """
    Return string similar to "rn4sr3"

    Lowercase and digits only.
    """
    return ''.join([
        random.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    ])
