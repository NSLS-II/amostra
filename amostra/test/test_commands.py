from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import deque
import time as ttime
import datetime
import pytz
import amostra.client.commands as amc
from amostra.testing import amostra_setup, amostra_teardown

from amostra.sample_data import *
import uuid

sample_uids = []
document_insertion_times = []

def teardown():
    amostra_teardown()

    
def setup():
    amostra_setup()
    global sample_uids, document_insertion_time
    document_insertion_time = ttime.time()
    # TODO: Get sample data!!!!!! and populate