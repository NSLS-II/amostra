import uuid
import time as ttime
import pytest
import time
from ..client.api import ContainerReference
from requests.exceptions import HTTPError, ConnectionError, RequestException
from ..testing import TESTING_CONFIG
from doct import Document

# TODO: Replace routines with a class for testing


def test_container_constructor():
    # attempt empty reference create
    s2 = ContainerReference()


def test_connection_switch(amostra_client):
    amostra_client.host = 'caesar'
    pytest.raises(RequestException, amostra_client)
    amostra_client.host = TESTING_CONFIG['host']
    amostra_client.port = TESTING_CONFIG['port']


def test_container_create(amostra_server, amostra_client):
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': str(uuid.uuid4())}
    cont1 = amostra_client.create(**ast_cont)
    assert cont1 == ast_cont['uid']


def test_duplicate_container(amostra_server, amostra_client):
    m_uid = str(uuid.uuid4())
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': m_uid}
    cont1 = amostra_client.create_container(**ast_cont)
    pytest.raises(HTTPError, amostra_client.create_container, uid=cont1)
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': 'some_unique_id'}


def test_invalid_container(amostra_server, amostra_client):
    inv_cont = dict(name='romans', uid=str(uuid.uuid4()),
                    time=str(ttime.time()), owner='obelix', project='invadegauls',
                    container=None,
                    beamline_id='trial_b')
    pytest.raises(HTTPError, amostra_client.create_container, **inv_cont)


def test_find_container(amostra_server, amostra_client):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = amostra_client.create_container(**f_cont)
    c_ret = next(amostra_client.find_container(uid=c_uid))
    assert c_ret['uid'] == c_uid


def test_find_container_as_doc(amostra_server, amostra_client):
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = amostra_client.create_container(**f_cont)
    c_ret_doc = next(amostra_client.find_container(uid=c_uid, as_document=True))
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid


def test_update_container(amostra_server, amostra_client):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = amostra_client.create_container(**orig_cont)
    amostra_client.update_container(query={'uid': orig_cont['uid']},
             update={'state': 'inactive','time': time.time()})
    updated_cont = next(amostra_client.find_container(uid=m_uid))
    assert updated_cont['state'] == 'inactive'


def test_update_container_illegal(amostra_server, amostra_client):
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    m_uid = amostra_client.create_container(**orig_cont)
    test_time = time.time()
    pytest.raises(HTTPError, amostra_client.update_container, query={'uid': orig_cont['uid']},
                  update={'uid': str(uuid.uuid4())})
