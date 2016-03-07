from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import deque
import time as ttime
import datetime
import uuid
import pytest
import pytz
import time
import amostra.client.commands as amc
from amostra.testing import amostra_setup, amostra_teardown
from amostra.client.api import SampleReference, RequestReference
from requests.exceptions import RequestException
import sys
from uuid import uuid4
from doct import Document

from amostra.sample_data import *
import uuid


def teardown():
    amostra_teardown()


def test_request_constructor():
    r1 = RequestReference()
    assert r1.host == 'localhost'
    assert r1.port == 7770
    

def test_req_connection_switch():
    r  = RequestReference()
    r.host = 'bogus_paigh'
    pytest.raises(RequestException, r.create)
    r.host = 'localhost'
    r.create()
    

def test_request_create():
    req1= RequestReference()
    req1.create()
    req2 = RequestReference()
    req2.create(sample=None, time=time.time(),
               uid=None, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')
    req2.host = 'bogus_paigh'
    pytest.raises(RequestException, req2.create)               
             
def test_duplicate_request():
    m_uid = str(uuid4())
    req1= RequestReference()
    req1.create(sample=None, time=time.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')
    req2 = RequestReference()
    pytest.raises(RequestException, req2.create, sample=None, time=time.time(),
               uid=m_uid, state='active', seq_num=0, foo='bar',
               hero='asterix', antihero='romans')

def test_request_find():
    r = RequestReference()
    req_dict = dict(sample=None, time=time.time(),
                    uid=None, state='active', seq_num=0, foo='bar',
                    hero='obelix', antihero='romans')     
    inserted = r.create(**req_dict)
    retrieved = next(r.find(foo='bar'))
    assert retrieved == inserted


def test_update_request():
    r = RequestReference()    
    m_uid = str(uuid4())
    req_dict = dict(sample=None, time=time.time(),
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