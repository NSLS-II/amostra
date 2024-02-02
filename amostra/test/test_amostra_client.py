from doct import Document
import time as ttime
import pytest
from ..testing import amostra_setup, amostra_teardown
from ..client.api import AmostraClient
from requests.exceptions import HTTPError, RequestException
from ..testing import TESTING_CONFIG

import uuid


def test_client_constructor(amostra_client):
    pytest.raises(TypeError, AmostraClient)


def test_connection_switch(amostra_client):
    amostra_client.host = 'caesar'
    pytest.raises(RequestException, amostra_client.create_sample, 'asterix')
    amostra_client.host = TESTING_CONFIG['host']


def test_sample_create(amostra_server, amostra_client):
   r1 = amostra_client.create_sample(name='test1')
   r2 = amostra_client.create_sample(name='test2', uid=str(uuid.uuid4()))
   m_kwargs = dict(owner='test', level='inferno', type='automated',
                   material='CoFeB')
   r3 = amostra_client.create_sample(name='test3', uid=str(uuid.uuid4()), **m_kwargs)


def test_invalid_sample(amostra_client):
    pytest.raises(TypeError, amostra_client.create_sample)


def test_find_sample(amostra_client):
    m_sample = dict(name='comp_samp', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='test', project='ci-tests',
                    beamline_id='test-ci')
    s = amostra_client.create_sample(**m_sample)
    s_ret = amostra_client.find_sample(uid=m_sample['uid'])
    assert s_ret[0]['uid'] == m_sample['uid']


def test_find_sample_as_doc(amostra_client):
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', container='legion1')
    amostra_client.create_sample(**m_sample)
    s_ret = amostra_client.find_sample(uid=m_sample['uid'], as_document=True)
    assert s_ret[0] == Document('Sample', m_sample)

def test_update_sample(amostra_client):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='arkilic', project='trial',
                       beamline_id='trial_b', state='active', container='legion2')
    amostra_client.create_sample(**test_sample)
    amostra_client.update_sample(query={'uid': test_sample['uid']},
                       update={'state': 'inactive', 'time': ttime.time()})
    updated_samp = amostra_client.find_sample(name='up_sam')[0]
    assert updated_samp['state'] == 'inactive'


def test_update_sample_illegal(amostra_client):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', updated=False)
    pytest.raises(HTTPError,
                  amostra_client.update_sample, query={'name': test_sample['name']},
                                      update={'uid': 'illegal'})

def test_container_create(amostra_client):
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': str(uuid.uuid4())}
    cont1 = amostra_client.create_container(**ast_cont)
    assert cont1 == ast_cont['uid']


def test_find_container(amostra_client):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = amostra_client.create_container(**f_cont)
    c_ret_doc = amostra_client.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid


def test_find_container_as_doc(amostra_client):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = amostra_client.create_container(**f_cont)
    c_ret_doc = amostra_client.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid

def test_update_container(amostra_client):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = amostra_client.create_container(**orig_cont)
    amostra_client.update_container(query={'uid': orig_cont['uid']},
                          update={'state': 'inactive','time': ttime.time()})
    updated_cont = amostra_client.find_container(uid=m_uid)[0]
    assert updated_cont['state'] == 'inactive'


def test_update_container_illegal(amostra_client):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = amostra_client.create_container(**orig_cont)
    test_time = ttime.time()
    pytest.raises(HTTPError, amostra_client.update_container, query={'uid': orig_cont['uid']},
                  update={'uid': str(uuid.uuid4())})


def test_request_create(amostra_client):
    amostra_client.create_request(sample='roman_sample', time=ttime.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')


def test_request_find(amostra_client):
    req_dict = dict(sample='hidefix', time=ttime.time(),
                    uid=str(uuid.uuid4()), state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    inserted = amostra_client.create_request(**req_dict)
    retrieved = amostra_client.find_request(uid=inserted)[0]
    assert retrieved['uid'] == inserted


def test_update_request(amostra_client):
    m_uid = str(uuid.uuid4())
    req_dict = dict(uid=m_uid, sample='hidefix', time=ttime.time(),
                    seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    amostra_client.create_request(**req_dict)
    amostra_client.update_request(query={'uid': m_uid},
                        update={'state': 'inactive'})
    updated_req = amostra_client.find_request(uid=m_uid)[0]
    assert updated_req['state'] == 'inactive'
