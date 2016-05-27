import time as ttime
import uuid
import pytest
from amostra.testing import amostra_local_setup, amostra_local_teardown
from amostra.client.local_commands import (LocalSampleReference,
                                           LocalContainerReference,
                                           LocalRequestReference)


def setup():
    amostra_local_setup()


def test_constructors():
    # attempt empty reference create
    s_ref = LocalSampleReference()
    c_ref = LocalContainerReference()
    r_ref = LocalRequestReference()


def test_create_sample():
    s = LocalSampleReference()
    s.create(uid=str(uuid.uuid4()), name='local roman',
             time=ttime.time(), compound='Fe', material='sword')


def test_create_request():
    r = LocalRequestReference()
    r.create(sample=None, time=ttime.time(), uid=str(uuid.uuid4()))


def test_create_container():
    c = LocalContainerReference()
    c.create(time=ttime.time(), uid=str(uuid.uuid4()), name='village',
             type='ancient gaul')


def test_find_sample():
    s = LocalSampleReference()
    samp_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='hidefix',
                     kind='dog', breed='multigree')
    s.create(**samp_dict)
    assert next(s.find(uid=samp_dict['uid']))['uid'] == samp_dict['uid']


def test_find_container():
    c = LocalContainerReference()
    cont_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='village',
                     kind='gaul', population='50')
    c.create(**cont_dict)
    assert next(c.find(uid=cont_dict['uid']))['uid'] == cont_dict['uid']


def test_find_request():
    r = LocalRequestReference()
    req_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='war',
                    kind='street fight', state='inactive', winner='gauls')
    r.create(**req_dict)
    assert next(r.find(uid=req_dict['uid']))['uid'] == req_dict['uid']


def test_update_sample():
    s = LocalSampleReference()
    samp = dict(uid=str(uuid.uuid4()), name='julius',
                time=ttime.time(), position='emperor', material='wisdom',
                state='in office')
    s.create(**samp)
    s.update({'uid': samp['uid']},
             {'state': 'murdered by brutus'})
    assert next(s.find(state='murdered by brutus'))['uid'] == samp['uid']


def test_update_container():
    c = LocalContainerReference()
    cont = dict(uid=str(uuid.uuid4()), container=str(uuid.uuid4()),
                time=ttime.time(),state='empty')

    c.create(**cont)
    c.update({'uid': cont['uid']},
             {'state': 'full'})
    assert next(c.find(uid=cont['uid']))['state'] == 'full'


def test_update_request():
    r = LocalRequestReference()
    req = dict(uid=str(uuid.uuid4()), sample=str(uuid.uuid4()),
                time=ttime.time(), scan='mesh')

    r.create(**req)
    r.update({'uid': req['uid']},
             {'scan': 'energy'})
    assert next(r.find(uid=req['uid']))['scan'] == 'energy'


def teardown():
    amostra_local_teardown()
