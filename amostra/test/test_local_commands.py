from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import time as ttime
import pytest
import uuid
# from amostra.testing import amostra_setup, amostra_teardown
from amostra.client.local_commands import (LocalSampleReference,
                                           LocalContainerReference,
                                           LocalRequestReference)
# TODO: Add local setup and teardown into testing

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
    pass


def test_create_container():
    pass


def test_find_sample():
    pass


def test_find_container():
    pass


def test_find_request():
    pass


