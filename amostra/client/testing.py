from pymongo import MongoClient
import time as ttime
from amostra.ignition import start_server
import uuid

TESTING_CONFIG = {
    'database': "mds_testing_disposable_{}".format(str(uuid.uuid4())),
    'mongo_host': 'localhost',
    'mongo_server': 'localhost',
    'mongo_port': 27017,
    'timezone': 'US/Eastern',
    'service_port;': 7770 }

def amostra_setup():
    start_server(config=TESTING_CONFIG)
    # ensure tornado server started prior to tests
    ttime.sleep(1)


def mds_teardown():
    global SERVICE_PROCESS
    if SERVICE_PROCESS is not None:
        SERVICE_PROCESS.terminate()
    SERVICE_PROCESS = None

    conn = MongoClient(TESTING_CONFIG['mongo_server'],
                       TESTING_CONFIG.get('mongo_port', None))
    conn.drop_database(TESTING_CONFIG['database'])