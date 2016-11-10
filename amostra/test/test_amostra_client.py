from doct import Document
import time as ttime
import pytest
from ..testing import amostra_setup, amostra_teardown
from ..client.api import AmostraClient
from requests.exceptions import HTTPError, RequestException
from ..testing import TESTING_CONFIG

import uuid


conn = AmostraClient(host=TESTING_CONFIG['host'],
                         port=TESTING_CONFIG['port'])


def teardown():
    amostra_teardown()

def test_client_constructor():
    pytest.raises(TypeError, AmostraClient)


def test_connection_switch(conn=conn):
    conn.host = 'caesar'
    pytest.raises(RequestException, conn.create_sample, 'asterix')
    conn.host = TESTING_CONFIG['host']


def test_sample_create(conn=conn):
   r1 = conn.create_sample(name='test1')
   r2 = conn.create_sample(name='test2', uid=str(uuid.uuid4()))
   m_kwargs = dict(owner='test', level='inferno', type='automated',
                   material='CoFeB')
   r3 = conn.create_sample(name='test3', uid=str(uuid.uuid4()), **m_kwargs)


def test_duplicate_sample(conn=conn):
    _com_uid = str(uuid.uuid4())
    conn.create_sample(name='test_sample', uid=_com_uid, custom=False)
    pytest.raises(HTTPError, conn.create_sample, name='test_duplicate',
                  uid=_com_uid)

