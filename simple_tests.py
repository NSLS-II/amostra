'''
Created on Feb 22, 2016

@author: arkilic
'''
from amostra.client.commands import SampleReference
import uuid

s = SampleReference([{'name':'sample1', 'uid':str(uuid.uuid4())}],
                    host='localhost', port=7770)
