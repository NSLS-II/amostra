from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import time as ttime
import pytest
import time
from ..testing import amostra_setup, amostra_teardown
from ..client.api import ContainerReference
from requests.exceptions import HTTPError, ConnectionError, RequestException
from ..testing import TESTING_CONFIG
from uuid import uuid4
from requests.exceptions import ConnectionError


def teardown():
    amostra_teardown()


def test_container_constructor():
    # attempt empty reference create
    s2 = ContainerReference()


def test_connection_switch():
    c = ContainerReference()
    c.host = 'caesar'
    pytest.raises(RequestException, c.create)
    c.host = TESTING_CONFIG['host']
    c.port = TESTING_CONFIG['port']
    c.create()


def test_container_create():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': str(uuid4())}
    cont1 = c.create(**ast_cont)
    assert cont1 == ast_cont['uid']


def test_duplicate_container():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    m_uid = str(uuid4())
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': m_uid}
    cont1 = c.create(**ast_cont)
    pytest.raises(HTTPError, c.create, uid=cont1)


def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate
