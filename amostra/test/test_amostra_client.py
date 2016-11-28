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
    assert s_ret[0]['uid'] == m_sample['uid']


def test_find_sample_as_doc(conn=conn):
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', container='legion1')
    conn.create_sample(**m_sample)
    s_ret = conn.find_sample(uid=m_sample['uid'], as_document=True)
    assert s_ret[0] == Document('Sample', m_sample)

def test_update_sample(conn=conn):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='arkilic', project='trial',
                       beamline_id='trial_b', state='active', container='legion2')
    conn.create_sample(**test_sample)
    conn.update_sample(query={'uid': test_sample['uid']},
                       update={'state': 'inactive', 'time': ttime.time()})
    updated_samp = conn.find_sample(name='up_sam')[0]
    assert updated_samp['state'] == 'inactive'


def test_update_sample_illegal(conn=conn):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', updated=False)
    pytest.raises(HTTPError,
                  conn.update_sample, query={'name': test_sample['name']},
                                      update={'uid': 'illegal'})

def test_container_create(conn=conn):
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': str(uuid.uuid4())}
    cont1 = conn.create_container(**ast_cont)
    assert cont1 == ast_cont['uid']


def test_find_container(conn=conn):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = conn.create_container(**f_cont)
    c_ret_doc = conn.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid


def test_find_container_as_doc(conn=conn):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = conn.create_container(**f_cont)
    c_ret_doc = conn.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid

def test_update_container(conn=conn):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = conn.create_container(**orig_cont)
    conn.update_container(query={'uid': orig_cont['uid']},
                          update={'state': 'inactive','time': ttime.time()})
    updated_cont = conn.find_container(uid=m_uid)[0]
    assert updated_cont['state'] == 'inactive'


def test_update_container_illegal(conn=conn):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = conn.create_container(**orig_cont)
    test_time = ttime.time()
    pytest.raises(HTTPError, conn.update_container, query={'uid': orig_cont['uid']},
                  update={'uid': str(uuid.uuid4())})


def test_request_create(conn=conn):
    conn.create_request(sample='roman_sample', time=ttime.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')


def test_duplicate_request(conn=conn):
    m_uid = str(uuid.uuid4())
    conn.create_request(sample='hidefix', time=ttime.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')
    pytest.raises(HTTPError, conn.create_request, sample='hidefix', time=ttime.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')

def test_request_find(conn=conn):
    req_dict = dict(sample='hidefix', time=ttime.time(),
                    uid=str(uuid.uuid4()), state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    inserted = conn.create_request(**req_dict)
    retrieved = conn.find_request(uid=inserted)[0]
    assert retrieved['uid'] == inserted


def test_update_request(conn=conn):
    m_uid = str(uuid.uuid4())
    req_dict = dict(uid=m_uid, sample='hidefix', time=ttime.time(),
                    seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    conn.create_request(**req_dict)
    conn.update_request(query={'uid': m_uid},
                        update={'state': 'inactive'})
    updated_req = conn.find_request(uid=m_uid)[0]
    assert updated_req['state'] == 'inactive'
