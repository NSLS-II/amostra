import time as ttime
import pytest
import time
from amostra.testing import amostra_setup, amostra_teardown
from amostra.client.api import RequestReference
from requests.exceptions import HTTPError, ConnectionError
from amostra.testing import TESTING_CONFIG
from uuid import uuid4
from requests.exceptions import ConnectionError

def teardown():
    amostra_teardown()


def test_request_constructor_config():
    r1 = RequestReference(host=TESTING_CONFIG['host'],
                          port=TESTING_CONFIG['port'])
    assert r1.host == TESTING_CONFIG['host']
    assert r1.port == TESTING_CONFIG['port']


def test_request_create():
    req1= RequestReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])

    req2 = RequestReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])
    req2.create(sample='roman_sample', time=time.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')


def test_duplicate_request():
    m_uid = str(uuid4())
    req1= RequestReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])
    req1.create(sample='hidefix', time=time.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')
    req2 = RequestReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])
    pytest.raises(HTTPError, req2.create, sample='hidefix', time=time.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')

def test_request_find():
    r = RequestReference(host=TESTING_CONFIG['host'],
                        port=TESTING_CONFIG['port'])
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=str(uuid4()), state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    inserted = r.create(**req_dict)
    retrieved = next(r.find(foo='bar'))
    assert retrieved['uid'] == inserted


def test_update_request():
    r = RequestReference(host=TESTING_CONFIG['host'],
                        port=TESTING_CONFIG['port'])
    m_uid = str(uuid4())
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=m_uid, state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    r.create(**req_dict)
    r.update(query={'uid': m_uid},
                       update={'state': 'inactive'})
    updated_req = next(r.find(uid=m_uid))
    assert updated_req['state'] == 'inactive'


def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate
