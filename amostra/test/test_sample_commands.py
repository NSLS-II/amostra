from doct import Document
import time as ttime
import pytest

from ..client.api import SampleReference, AmostraClient
from requests.exceptions import HTTPError, RequestException
from ..testing import TESTING_CONFIG

import uuid

sample_uids = []
document_insertion_times = []


def test_sample_constructor():
    s2 = SampleReference()


def test_connection_switch(amostra_server, amostra_client):
    amostra_client.host = 'caesar'
    pytest.raises(RequestException, amostra_client._sample_client.create, 'asterix')
    amostra_client.host = TESTING_CONFIG['host']
    amostra_client._sample_client.create(name='asterix')


def test_sample_create(amostra_server, amostra_client):
    r1 = amostra_client._sample_client.create(name='test1')
    r2 = amostra_client._sample_client.create(name='test2', uid=str(uuid.uuid4()))
    m_kwargs = dict(owner='test', level='inferno', type='automated',
                    material='CoFeB')
    r3 = amostra_client._sample_client.create(name='test3', uid=str(uuid.uuid4()), **m_kwargs)


def test_invalid_sample(amostra_server, amostra_client):
    pytest.raises(TypeError, amostra_client._sample_client.create)


def test_find_sample(amostra_server, amostra_client):
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    container='test_group1',
                    beamline_id='trial_b')

    amostra_client._sample_client.create(**m_sample)

    s_ret = next(amostra_client._sample_client.find(uid=m_sample['uid']))
    assert s_ret == m_sample


def test_find_sample_as_doc(amostra_server, amostra_client):
    m_sample = dict(name='comp_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', container='legion1')
    amostra_client._sample_client.create(**m_sample)
    s_ret = next(amostra_client._sample_client.find(uid=m_sample['uid'], as_document=True))
    assert s_ret == Document('Sample', m_sample)


def test_update_sample(amostra_server, amostra_client):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                       time=ttime.time(), owner='arkilic', project='trial',
                       beamline_id='trial_b', state='active', container='legion2')
    amostra_client._sample_client.create(**test_sample)
    amostra_client._sample_client.update(query={'uid': test_sample['uid']},
                update={'state': 'inactive', 'time': ttime.time()})
    updated_samp = next(amostra_client._sample_client.find(name='up_sam'))
    assert updated_samp['state'] == 'inactive'

def test_update_sample_illegal(amostra_server, amostra_client):
    test_sample = dict(name='up_sam', uid=str(uuid.uuid4()),
                    time=ttime.time(), owner='arkilic', project='trial',
                    beamline_id='trial_b', updated=False)
    pytest.raises(HTTPError,
                  amostra_client._sample_client.update, query={'name': test_sample['name']},
                                      update={'uid': 'illegal'})
