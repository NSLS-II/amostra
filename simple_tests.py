from amostra.client.commands import SampleReference, RequestReference
import uuid
import time
from requests.exceptions import HTTPError

m_sample = dict(name='m_sample', uid=str(uuid.uuid4()), 
                time=time.time(), owner='arkilic', project='trial',
                beamline_id='trial_b')
s1 = SampleReference([m_sample],
                    host='localhost', port=7770)
r = s1.create(name='2nd')
print('Sample has been created', r)
crsr = s1.find(name='m_sample')
try:
    s1.update(query={'uid':m_sample['uid']}, update={'time':0.00003})
except HTTPError:
    print('Caught the appropriate update error')
req1 = RequestReference(sample=m_sample, host='localhost', port=7770)
req1.create(sample=m_sample, host='localhost', port=7770)
s2 = SampleReference()
print('Trying to update reference state')
req1.update(query={'sample': m_sample['uid']}, update={'state': 'inactive'})
if next(req1.find(state='inactive')):
    print('Successfully updated the request state')