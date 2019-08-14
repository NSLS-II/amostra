import pytest


@pytest.fixture()
def url():
    url = 'mongodb://localhost:27017/'
    return url
