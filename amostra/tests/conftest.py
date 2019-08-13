import amostra.mongo_client
from pymongo import MongoClient
import pytest


@pytest.fixture()
def client_conf():
    def conf():
        connection = MongoClient('localhost', 27017)
        db = connection['tests-amostra']
        db['samples'].drop()
        db['samples_revisions'].drop()
        client = amostra.mongo_client.Client('mongodb://localhost:27017/tests-amostra')
        mongo_client = MongoClient('mongodb://localhost:27017/')
        return client, mongo_client
    return conf
