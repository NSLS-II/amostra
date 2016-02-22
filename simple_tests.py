'''
Created on Feb 22, 2016

@author: arkilic
'''
from amostra.client.commands import SampleReference
import uuid
import time
m_sample = dict(name='m_sample', uid=str(uuid.uuid4()), 
                time=time.time(), owner='arkilic', project='trial',
                beamline_id='trial_b')

s = SampleReference([m_sample],
                    host='localhost', port=7770)
