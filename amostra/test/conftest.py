import uuid
import pytest
import subprocess
import contextlib
import time as ttime
import sys

from amostra.client.commands import AmostraClient

testing_config = {
    "database": "mds_testing_disposable_{}".format(str(uuid.uuid4())),
    "mongo_server": "localhost",
    "mongo_uri": "mongodb://localhost",
    "mongo_port": 27017,
    "host": "localhost",
    "port": 7770,
    "timezone": "US/Eastern",
    "mongo_user": "tom",
    "mongo_pwd": "jerry",
    "local_files": "~/amostra_files",
}


@contextlib.contextmanager
def astore_startup():
    try:
        ps = subprocess.Popen(
            [
                sys.executable,
                "-c",
                f"from amostra.ignition import start_server; start_server(config={testing_config}, testing=True) ",
            ],
        )
        ttime.sleep(1.3)  # make sure the process is started
        yield ps
    finally:
        ps.terminate()

@pytest.fixture(scope="session")
def astore_server():
    with astore_startup() as astore_fixture:
        yield


@pytest.fixture(scope="function")
def astore_client():
    conn = AmostraClient(host=testing_config["host"], port=testing_config["port"])
    return conn
