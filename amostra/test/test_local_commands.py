import time as ttime
import uuid
import pytest
from amostra.client.local_commands import (LocalSampleReference,
                                           LocalContainerReference,
                                           LocalRequestReference)


def test_constructors():
    # attempt empty reference create
    s_ref = LocalSampleReference()
    c_ref = LocalContainerReference()
    r_ref = LocalRequestReference()


def test_create_sample(amostra_local_sample):
    amostra_local_sample.create(uid=str(uuid.uuid4()), name='local roman',
             time=ttime.time(), compound='Fe', material='sword')


def test_create_request(amostra_local_request):
    amostra_local_request.create(sample=None, time=ttime.time(), uid=str(uuid.uuid4()))


def test_create_container(amostra_local_container):
    amostra_local_container.create(time=ttime.time(), uid=str(uuid.uuid4()), name='village',
             type='ancient gaul')


def test_find_sample(amostra_local_sample):
    samp_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='hidefix',
                     kind='dog', breed='multigree')
    amostra_local_sample.create(**samp_dict)
    assert next(amostra_local_sample.find(uid=samp_dict['uid']))['uid'] == samp_dict['uid']


def test_find_container(amostra_local_container):
    cont_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='village',
                     kind='gaul', population='50')
    amostra_local_container.create(**cont_dict)
    assert next(amostra_local_container.find(uid=cont_dict['uid']))['uid'] == cont_dict['uid']


def test_find_request(amostra_local_request):
    req_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='war',
                    kind='street fight', state='inactive', winner='gauls')
    amostra_local_request.create(**req_dict)
    assert next(amostra_local_request.find(uid=req_dict['uid']))['uid'] == req_dict['uid']


def test_update_sample(amostra_local_sample):
    samp = dict(uid=str(uuid.uuid4()), name='julius',
                time=ttime.time(), position='emperor', material='wisdom',
                state='in office')
    amostra_local_sample.create(**samp)
    amostra_local_sample.update({'uid': samp['uid']},
             {'state': 'murdered by brutus'})
    assert next(amostra_local_sample.find(state='murdered by brutus'))['uid'] == samp['uid']


def test_update_container(amostra_local_container):
    cont = dict(uid=str(uuid.uuid4()), container=str(uuid.uuid4()),
                time=ttime.time(),state='empty')

    amostra_local_container.create(**cont)
    amostra_local_container.update({'uid': cont['uid']},
             {'state': 'full'})
    assert next(amostra_local_container.find(uid=cont['uid']))['state'] == 'full'


def test_update_request(amostra_local_request):
    req = dict(uid=str(uuid.uuid4()), sample=str(uuid.uuid4()),
                time=ttime.time(), scan='mesh')

    amostra_local_request.create(**req)
    amostra_local_request.update({'uid': req['uid']},
             {'scan': 'energy'})
    assert next(amostra_local_request.find(uid=req['uid']))['scan'] == 'energy'
