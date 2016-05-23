from pymongo import MongoClient
import time as ttime
from amostra.ignition import start_server
import uuid
import pytest
import subprocess

# TODO: Add a test data factory module here


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
    # TODO: Replace this with Popen instead of command line
    ttime.sleep(1)


def amostra_teardown():
    conn = MongoClient('{}:{}'.format(TESTING_CONFIG['mongo_server'],
                                      TESTING_CONFIG['mongo_port']))
    conn.amostra.drop_collection('sample')


class _baseSM:    
    #    @classmethod
    #def setup_class(cls):
    #    db = cls.db = cls.db_class(*cls.args, **cls.kwargs)

    #def test_create_and_find(self):
    #    db = self.db
    #    aarduid = str(uuid.uuid4())
    #    doc = db.create(name='Lionel', location='zoo', species='aardvark',
    #                    uid=aarduid)
    #    find_res = list(db.find({'uid': aarduid}))
    #    assert len(find_res) == 1
    #    assert find_res[0]['uid'] == aarduid

    def test_update(self):
        db = self.db
        sam_uid = str(uuid.uuid4())
        uid = db.create(name='samantha', location='home', occupation='zoo goer',
                        uid=sam_uid)
    #     original = list(db.find(uid=uid))[0]
    #     old, new = db.update(uid, location='zoo')
    #     assert old == original
    #     assert new['location'] == 'zoo'
    # 
    #     with pytest.raises(ValueError):
    #         db.update(uid, name='casper')
    # 
    # def test_find(self):
    #     def _helper(kwargs, n):
    #         ret = list(self.db.find(**kwargs))
    #         assert len(ret) == n
    # 
    #     t_vals = [({'family': 'bird'}, 6),
    #               ({'species': 'penguin'}, 3),
    #               ({'species': 'puffin'}, 3),
    #               ({'location': 'zoo', 'family': 'bird'}, 3)]
    # 
    #     for kw, n in t_vals:
    #         yield _helper, kw, n
    # 
    # def test_add_fail(self):
    #     db = self.db
    #     with pytest.raises(ValueError):
    #         db.add(name='Fredrick', color='gray')
    # 
    # def test_update_overwrite(self):
    #     db = self.db
    #     uid = db.add(name='linkt', location='VR')
    #     with pytest.raises(ValueError):
    #         db.update(uid, overwrite=False, location='R')

    @classmethod
    def teardown_class(cls):
        conn = MongoClient('localhost:27017')
        conn.amostra.drop_collection('sample')
