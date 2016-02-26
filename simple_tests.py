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
s1.update(query={'uid':m_sample['uid']}, update={'time':0.00003})

req1 = RequestReference(sample=m_sample, host='localhost', port=7770)
req1.create(sample=m_sample, host='localhost', port=7770)

s2 = SampleReference()

print(m_sample['uid'])
req1.update(query={'sample': m_sample['uid']}, update={'time': 1})

print(next(req1.find(time=1)))
print(next(s1.find(time=0.00003)))

t = time.time()

res = s1.update(query={'time': 0.00003}, update={'time': t})
print(list(s1.find(time=t)))