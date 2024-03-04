import uuid
import pytest
import subprocess
import contextlib
import os
from pathlib import Path
import time as ttime
import shutil
import sys

from amostra.client.commands import AmostraClient
from amostra.client.local_commands import (
    LocalContainerReference,
    LocalRequestReference,
    LocalSampleReference,
)

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
    "local_files": "/tmp/amostra_files",
}


@contextlib.contextmanager
def amostra_startup():
    try:
        ps = subprocess.Popen(
            [
                sys.executable,
                "-c",
                f"from amostra.ignition import start_server; start_server(config={testing_config}, testing=True)",
            ],
        )
        print(f"entire command: from amostra.ignition import start_server; start_server(config={testing_config}, testing=True)")
        ttime.sleep(1.3)  # make sure the process is started
        yield ps
    finally:
        ps.terminate()


@pytest.fixture(scope="session")
def amostra_server():
    with amostra_startup() as amostra_fixture:
        yield


@pytest.fixture(scope="function")
def amostra_client():
    conn = AmostraClient(host=testing_config["host"], port=testing_config["port"])
    return conn


@pytest.fixture(scope="function")
def amostra_local_container(request):
    try:
        usr_path = os.path.expanduser(testing_config["local_files"])
        os.mkdir(usr_path)
    except FileExistsError:
        pass
    local_container = LocalContainerReference(top_dir=testing_config["local_files"])

    def clear_files():
        try:
            shutil.rmtree(Path(testing_config["local_files"]).expanduser())
        except FileNotFoundError:
            pass

    request.addfinalizer(lambda: clear_files())
    return local_container


@pytest.fixture(scope="function")
def amostra_local_request(request):
    try:
        usr_path = os.path.expanduser(testing_config["local_files"])
        os.mkdir(usr_path)
    except FileExistsError:
        pass
    local_request = LocalRequestReference(top_dir=testing_config["local_files"])

    def clear_files():
        try:
            shutil.rmtree(Path(testing_config["local_files"]).expanduser())
        except FileNotFoundError:
            pass

    request.addfinalizer(lambda: clear_files())
    return local_request


@pytest.fixture(scope="function")
def amostra_local_sample(request):
    try:
        usr_path = os.path.expanduser(testing_config["local_files"])
        os.mkdir(usr_path)
    except FileExistsError:
        pass
    local_sample = LocalSampleReference(top_dir=testing_config["local_files"])

    def clear_files():
        try:
            shutil.rmtree(Path(testing_config["local_files"]).expanduser())
        except FileNotFoundError:
            pass

    request.addfinalizer(lambda: clear_files())
    return local_sample
