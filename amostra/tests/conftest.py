import amostra.mongo_client
from pymongo import MongoClient
import pytest


connection = MongoClient('localhost', 27017)
db = connection['tests-amostra']
db['samples'].drop()
db['samples_revisions'].drop()


@pytest.fixture()
def client():
    client = amostra.mongo_client.Client('mongodb://localhost:27017/tests-amostra')
    return client
