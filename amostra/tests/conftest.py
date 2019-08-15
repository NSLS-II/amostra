import amostra.mongo_client
import pytest
import uuid
from pymongo import MongoClient


@pytest.fixture()
def client():
    url = 'mongodb://localhost:27017/'
    db_name = str(uuid.uuid4())
    client = amostra.mongo_client.Client(url + db_name)
    yield client
    #Clean db at the end of whole test function
    MongoClient(url).drop_database(db_name)
