import uuid
import time as ttime
import pytest
import time
from ..testing import amostra_setup, amostra_teardown
from ..client.api import ContainerReference
from requests.exceptions import HTTPError, ConnectionError, RequestException
from ..testing import TESTING_CONFIG
from doct import Document

# TODO: Replace routines with a class for testing


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
                'container': 'gauls', 'uid': str(uuid.uuid4())}
    cont1 = c.create(**ast_cont)
    assert cont1 == ast_cont['uid']


def test_duplicate_container():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    m_uid = str(uuid.uuid4())
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': m_uid}
    cont1 = c.create(**ast_cont)
    pytest.raises(HTTPError, c.create, uid=cont1)
    ast_cont = {'name': 'obelix', "dog": 'hidefix', 'time': ttime.time(),
                'container': 'gauls', 'uid': 'some_unique_id'}


def test_invalid_container():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    inv_cont = dict(name='romans', uid=str(uuid.uuid4()),
                    time=str(ttime.time()), owner='obelix', project='invadegauls',
                    container=None,
                    beamline_id='trial_b')
    pytest.raises(HTTPError, c.create, **inv_cont)


def test_find_container():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = c.create(**f_cont)
    c_ret = next(c.find(uid=c_uid))
    assert c_ret['uid'] == c_uid


def test_find_container_as_doc():
    c = ContainerReference(TESTING_CONFIG['host'], TESTING_CONFIG['port'])
    f_cont = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='hidefix', project='ceasar',
                    container='gauls',
                    beamline_id='fiction')
    c_uid = c.create(**f_cont)
    c_ret_doc = next(c.find(uid=c_uid, as_document=True))
    assert Document == type(c_ret_doc)
    assert c_ret_doc['uid'] == c_uid


def test_update_container():
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    c = ContainerReference(host=TESTING_CONFIG['host'],
                              port=TESTING_CONFIG['port'])
    m_uid = c.create(**orig_cont)
    c.update(query={'uid': orig_cont['uid']},
             update={'state': 'inactive','time': time.time()})
    updated_cont = next(c.find(uid=m_uid))
    assert updated_cont['state'] == 'inactive'


def test_update_container_illegal():
    orig_cont = dict(name='obelix', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='chief', project='egypt',
                       beamline_id='fiction', state='active', container='SPQR')
    c = ContainerReference(host=TESTING_CONFIG['host'],
                              port=TESTING_CONFIG['port'])
    m_uid = c.create(**orig_cont)
    test_time = time.time()
    pytest.raises(HTTPError, c.update, query={'uid': orig_cont['uid']},
                  update={'uid': str(uuid.uuid4())})


def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate
