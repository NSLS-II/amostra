import time
from amostra.client.api import RequestReference
from amostra.testing import TESTING_CONFIG
from uuid import uuid4


def test_request_create(amostra_server, amostra_client):
    amostra_client._request_client.create(sample='roman_sample', time=time.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')


def test_request_find(amostra_server, amostra_client):
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=str(uuid4()), state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    inserted = amostra_client._request_client.create(**req_dict)
    retrieved = next(amostra_client._request_client.find(foo='bar'))
    assert retrieved['uid'] == inserted


def test_update_request(amostra_server, amostra_client):
    m_uid = str(uuid4())
    req_dict = dict(sample='hidefix', time=time.time(),
                    uid=m_uid, state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')
    amostra_client._request_client.create(**req_dict)
    amostra_client._request_client.update(query={'uid': m_uid},
                       update={'state': 'inactive'})
    updated_req = next(amostra_client._request_client.find(uid=m_uid))
    assert updated_req['state'] == 'inactive'
