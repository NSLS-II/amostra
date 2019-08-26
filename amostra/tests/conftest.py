import uuid

import pytest
from pymongo import MongoClient

import amostra.mongo_client


@pytest.fixture()
def client():
    url = 'mongodb://localhost:27017/'
    db_name = str(uuid.uuid4())
    client = amostra.mongo_client.Client(url + db_name)
    yield client
    # Clean db at the end of whole test function.
    MongoClient(url).drop_database(db_name)
