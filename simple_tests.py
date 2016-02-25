from amostra.client.commands import SampleReference, RequestReference
import uuid
import time
m_sample = dict(name='m_sample', uid=str(uuid.uuid4()), 
                time=time.time(), owner='arkilic', project='trial',
                beamline_id='trial_b')
s1 = SampleReference([m_sample],
                    host='localhost', port=7770)
r = s1.add(name='2nd')
print('Sample has been created', r)
crsr = s1.find(name='m_sample')
print(list(crsr))

req1 = RequestReference(sample=m_sample, host='localhost', port=7770)
req1.create_request(sample=m_sample, host='localhost', port=7770)

s2 = SampleReference()

req1.update(filter={'sample': m_sample['uid']}, update={'time': 0})