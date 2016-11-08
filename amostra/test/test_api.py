# Smoketest the api
from amostra.client.api import (SampleReference, RequestReference,
                                ContainerReference, AmostraClient)

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

    create_samp = AmostraClient.create_sample
    create_cont = AmostraClient.create_container
    create_cont = AmostraClient.create_request

    find_samp = AmostraClient.find_sample
    find_cont = AmostraClient.find_container
    find_req = AmostraClient.find_request

    update_samp = AmostraClient.update_sample
    update_cont = AmostraClient.update_container
    update_req = AmostraClient.update_request
