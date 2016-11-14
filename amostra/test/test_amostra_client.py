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


def test_invalid_sample(conn=conn):
    pytest.raises(TypeError, conn.create_sample)


def test_find_sample(conn=conn):
    m_sample = dict(name='comp_samp', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='test', project='ci-tests',
                    beamline_id='test-ci')
    s = conn.create_sample(**m_sample)
    s_ret = conn.find_sample(uid=m_sample['uid'])
    assert s_ret == m_sample


def test_find_sample_as_doc(conn=conn):
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', container='legion1')
    conn.create_sample(**m_sample)
    s_ret = conn.find_sample(uid=m_sample['uid'], as_document=True)
    assert s_ret == Document('Sample', m_sample)

def test_update_sample():
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='arkilic', project='trial',
                       beamline_id='trial_b', state='active', container='legion2')
    conn.create_sample(**test_sample)
    conn.update_sample(query={'uid': test_sample['uid']},
                       update={'state': 'inactive', 'time': ttime.time()})
    updated_samp = conn.find_sample(name='up_sam'))
    assert updated_samp['state'] == 'inactive'
