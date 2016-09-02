from pymongo import MongoClient
import time as ttime
from amostra.ignition import start_server
import uuid
import os
import shutil

TESTING_CONFIG = {
    'database': "mds_testing_disposable_{}".format(str(uuid.uuid4())),
    'mongo_server': 'localhost',
    'mongo_port': 27017,
    'host': 'localhost',
    'port': 7770,
    'timezone': 'US/Eastern',
    'mongo_user': 'tom',
    'mongo_pwd': 'jerry',
    'local_files': '~/amostra_files'}


def amostra_setup():
    # start_server(config=TESTING_CONFIG)
    # ensure tornado server started prior to tests
    ttime.sleep(1)


def amostra_teardown():
    uri = 'mongodb://{0}:{1}@{2}:{3}/'.format(TESTING_CONFIG['mongo_user'],
                                              TESTING_CONFIG['mongo_pwd'],
                                              TESTING_CONFIG['mongo_server'],
                                              TESTING_CONFIG['mongo_port'])
    conn = MongoClient(uri)
    conn.amostra.drop_collection('sample')
    conn.amostra.drop_collection('request')
    conn.amostra.drop_collection('container')


def amostra_local_setup():
    try:
        usr_path = os.path.expanduser(TESTING_CONFIG['local_files'])
        os.mkdir(usr_path)
    except FileExistsError:
        pass


def amostra_local_teardown():
    try:
        shutil.rmtree(TESTING_CONFIG['local_files'])
    except FileNotFoundError:
        pass


class _baseSM:
    @classmethod
    def test_create(self):
        db = self.db
        ast_uid = str(uuid.uuid4())
        uid = db.create(name='obelix', location='gaul', occupation='hero',
                        uid=ast_uid)
