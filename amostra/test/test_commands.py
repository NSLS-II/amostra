from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import deque
import time as ttime
import datetime
import uuid
import pytest
import pytz
import amostra.client.commands as amc
from amostra.testing import amostra_setup, amostra_teardown
from amostra.client.api import SampleReference, RequestReference
from requests.exceptions import HTTPError

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


def test_sample_create():
    samp = SampleReference()
    r1 = samp.create(name='test1')
    r2 = samp.create(name='test2', uid=str(uuid.uuid4()))
    m_kwargs = dict(owner='test', level='inferno', type='automated',
                    material='CoFeB')
    r3 = samp.create(name='test3', uid=str(uuid.uuid4()), **m_kwargs)

def test_duplicate_sample():
    # d = dict(name='test_dup')
    s = SampleReference()
    r1 = s.create(name='test_dup', uid=str(uuid.uuid4()))
    pytest.raises(ValueError, s.create, name='test_dup')

def test_invalid_sample():
    s = SampleReference()
    pytest.raises(TypeError, s.create)

def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate