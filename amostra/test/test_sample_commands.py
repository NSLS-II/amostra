from doct import Document
import time as ttime
import pytest

from ..testing import amostra_setup, amostra_teardown
from ..client.api import SampleReference, AmostraClient
from requests.exceptions import HTTPError, RequestException
from ..testing import TESTING_CONFIG

import uuid

sample_uids = []
document_insertion_times = []

def teardown():
    amostra_teardown()


def test_sample_constructor():
    s2 = SampleReference()


def test_connection_switch():
    s = SampleReference()
    s.host = 'caesar'
    pytest.raises(RequestException, s.create, 'asterix')
    s.host = TESTING_CONFIG['host']
    s.create(name='asterix')


def test_sample_create():
    samp = SampleReference()
    samp.host = TESTING_CONFIG['host']
    samp.port = TESTING_CONFIG['port']
    r1 = samp.create(name='test1')
    r2 = samp.create(name='test2', uid=str(uuid.uuid4()))
    m_kwargs = dict(owner='test', level='inferno', type='automated',
                    material='CoFeB')
    r3 = samp.create(name='test3', uid=str(uuid.uuid4()), **m_kwargs)


def test_duplicate_sample():
    s = SampleReference(host=TESTING_CONFIG['host'],
                        port=TESTING_CONFIG['port'])
    _comm_uid = str(uuid.uuid4())
    s.create(name='test_samp', uid=_comm_uid)
    pytest.raises(HTTPError, s.create, name='test_dup', uid=_comm_uid)


def test_invalid_sample():
    s = SampleReference(host=TESTING_CONFIG['host'],
                        port=TESTING_CONFIG['port'])
    pytest.raises(TypeError, s.create)


def test_find_sample():
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    container='test_group1',
                    beamline_id='trial_b')

    s1 = SampleReference(host=TESTING_CONFIG['host'],
                         port=TESTING_CONFIG['port'])
    s1.create(**m_sample)

    s_ret = next(s1.find(uid=m_sample['uid']))
    assert s_ret == m_sample


def test_find_sample_as_doc():
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', container='legion1')
    s1 = SampleReference(host=TESTING_CONFIG['host'],
                         port=TESTING_CONFIG['port'])
    s1.create(**m_sample)
    s_ret = next(s1.find(uid=m_sample['uid'], as_document=True))
    assert s_ret == Document('Sample', m_sample)


def test_update_sample():
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='arkilic', project='trial',
                       beamline_id='trial_b', state='active', container='legion2')
    samp = SampleReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])
    samp.create(**test_sample)
    samp.update(query={'uid': test_sample['uid']},
                update={'state': 'inactive', 'time': ttime.time()})
    updated_samp = next(samp.find(name='up_sam'))
    assert updated_samp['state'] == 'inactive'

def test_update_sample_illegal():
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', updated=False)
    samp = SampleReference(host=TESTING_CONFIG['host'],
                           port=TESTING_CONFIG['port'])
    pytest.raises(HTTPError,
                  samp.update, query={'name': test_sample['name']},
                                      update={'uid': 'illegal'})


def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate
