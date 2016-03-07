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
import sys
from doct import Document

from amostra.sample_data import *
import uuid


def teardown():
    amostra_teardown()

def test_request_constructor():
    r1 = RequestReference(host='localhost', port=7770)
        
    
def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate