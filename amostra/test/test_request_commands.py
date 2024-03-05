import time
from amostra.client.api import RequestReference
from amostra.testing import TESTING_CONFIG
from uuid import uuid4


def test_request_create(amostra_server, amostra_client):
    amostra_client.create_request(sample='roman_sample', time=time.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')


def test_request_find(amostra_server, amostra_client):
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=str(uuid4()), state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    inserted = amostra_client.create_request(**req_dict)
    retrieved = amostra_client.find_request(foo='bar')[0]
    assert retrieved['uid'] == inserted


def test_update_request(amostra_server, amostra_client):
    m_uid = str(uuid4())
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=m_uid, state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    amostra_client.create_request(**req_dict)
    amostra_client.update_request(query={'uid': m_uid},
                       update={'state': 'inactive'})
    updated_req = amostra_client.find_request(uid=m_uid)[0]
    assert updated_req['state'] == 'inactive'
