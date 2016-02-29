# Smoketest the api
from amostra.client.api import SampleReference
from amostra.client.api import RequestReference

def test_api_smoke():
    s_create = SampleReference.create
    s_find = SampleReference.find
    s_update = SampleReference.update
    s_getyaml = SampleReference.dump_to_yaml
    s_getjson = SampleReference.dump_to_json
    
    r_create = RequestReference.create
    r_find = RequestReference.find
    r_update = RequestReference.update