'''
Created on Feb 22, 2016

@author: arkilic
'''
from amostra.client.commands import SampleReference, RequestReference
import uuid
import time
m_sample = dict(name='m_sample', uid=str(uuid.uuid4()), 
                time=time.time(), owner='arkilic', project='trial',
                beamline_id='trial_b')

s1 = SampleReference([m_sample],
                    host='localhost', port=7770)

r = s1.add(name='2nd')
print(r)

crsr = s1.find(name='m_sample')

samp = next(crsr)

print(samp)
req1 = RequestReference(samp, host='localhost', port=7770)