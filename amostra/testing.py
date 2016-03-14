from pymongo import MongoClient
import time as ttime
from amostra.ignition import start_server
import uuid
import pytest


TESTING_CONFIG = {
    'database': "mds_testing_disposable_{}".format(str(uuid.uuid4())),
    'mongo_server': 'localhost',
    'mongo_port': 27017,
    'host': 'localhost',
    'port': 7770,
    'timezone': 'US/Eastern'}


def amostra_setup():
    #start_server(config=TESTING_CONFIG)
    # ensure tornado server started prior to tests
    ttime.sleep(1)


def amostra_teardown():
    conn = MongoClient(TESTING_CONFIG['mongo_server'],
                       TESTING_CONFIG.get('mongo_port', None))
    conn.drop_database(TESTING_CONFIG['database'])