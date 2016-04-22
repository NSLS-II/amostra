# Smoketest the api
from amostra.client.api import (SampleReference, RequestReference, 
                                ContainerReference)

def test_api_smoke():
    s_create = SampleReference.create
    s_find = SampleReference.find
    s_update = SampleReference.update
    
    r_create = RequestReference.create
    r_find = RequestReference.find
    r_update = RequestReference.update
    
    c_create = ContainerReference.create
    r_find = ContainerReference.find
    r_update = ContainerReference.update