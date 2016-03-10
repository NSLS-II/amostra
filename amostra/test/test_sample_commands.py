from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import deque
import time as ttime
import datetime
import uuid
import pytest
import pytz
from copy import deepcopy
import amostra.client.commands as amc
from amostra.testing import amostra_setup, amostra_teardown
from amostra.client.api import (SampleReference, RequestReference,
                                ContainerReference)
from requests.exceptions import HTTPError, RequestException
import sys
from doct import Document

from amostra.sample_data import *
import uuid

sample_uids = []
document_insertion_times = []

def teardown():
    amostra_teardown()

    
def test_sample_constructor():
    pytest.raises(TypeError, SampleReference, 'InvalidTypeForStr')
    m_sample = dict(name='m_sample', uid=str(uuid.uuid4()), 
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b')
    s1 = SampleReference([m_sample],
                         host='localhost', port=7770)
    s2 = SampleReference()


def test_connection_switch():
    s = SampleReference()
    s.host = 'bogus_paigh'
    pytest.raises(RequestException, s.create, 'asterix')
    s.host = 'localhost'
    s.create(name='asterix')

def test_sample_create():
    samp = SampleReference()
    r1 = samp.create(name='test1')
    r2 = samp.create(name='test2', uid=str(uuid.uuid4()))
    m_kwargs = dict(owner='test', level='inferno', type='automated',
                    material='CoFeB')
    r3 = samp.create(name='test3', uid=str(uuid.uuid4()), **m_kwargs)


def test_duplicate_sample():
    s = SampleReference()
    r1 = s.create(name='test_dup', uid=str(uuid.uuid4()))
    pytest.raises(ValueError, s.create, name='test_dup')


def test_invalid_sample():
    s = SampleReference()
    pytest.raises(TypeError, s.create)


def test_find_sample():
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()), 
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b')
    s1 = SampleReference([m_sample],
                         host='localhost', port=7770)
    s_ret = next(s1.find(uid=m_sample['uid']))    
    assert s_ret == m_sample


def test_find_sample_as_doc():
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()), 
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b')
    s1 = SampleReference([m_sample],
                         host='localhost', port=7770)
    s_ret = next(s1.find(uid=m_sample['uid'], as_document=True))
    assert s_ret == Document('sample', m_sample)


def test_update_sample():
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()), 
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', state='active')
    samp = SampleReference([test_sample],
                         host='localhost', port=7770)
    samp.update(query={'name': test_sample['name']}, 
                       update={'state': 'inactive'})
    updated_samp = next(samp.find(name='up_sam'))
    assert updated_samp['state'] == 'inactive'   
    

def test_update_sample_illegal():
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()), 
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', updated=False)
    samp = SampleReference([test_sample],
                         host='localhost', port=7770)
    pytest.raises(HTTPError,
                  samp.update, query={'name': test_sample['name']},
                                      update={'time': 'illegal'})
    pytest.raises(HTTPError,
                  samp.update, query={'name': test_sample['name']},
                                      update={'name': 'illegal'})
    pytest.raises(HTTPError,
                  samp.update, query={'name': test_sample['name']},
                                      update={'uid': 'illegal'})


def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate