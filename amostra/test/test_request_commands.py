import time
from amostra.client.api import RequestReference
from amostra.testing import TESTING_CONFIG
from uuid import uuid4


def test_request_constructor_config(amostra_server, amostra_client):
    amostra_client = RequestReference(
        host=TESTING_CONFIG["host"], port=TESTING_CONFIG["port"]
    )
    assert amostra_client.host == TESTING_CONFIG["host"]
    assert amostra_client.port == TESTING_CONFIG["port"]


def test_request_create(amostra_server, amostra_client):
    amostra_client = RequestReference(
        host=TESTING_CONFIG["host"], port=TESTING_CONFIG["port"]
    )

    req2 = RequestReference(host=TESTING_CONFIG["host"], port=TESTING_CONFIG["port"])
    req2.create(
        sample="roman_sample",
        time=time.time(),
        uid=None,
        state="active",
        seq_num=0,
        foo="bar",
        hero="asterix",
        antihero="romans",
    )


def test_request_find(amostra_server, amostra_client):
    amostra_client = RequestReference(
        host=TESTING_CONFIG["host"], port=TESTING_CONFIG["port"]
    )
    req_dict = dict(
        sample="hidefix",
        time=time.time(),
        uid=str(uuid4()),
        state="active",
        seq_num=0,
        foo="bar",
        hero="obelix",
        antihero="romans",
    )
    inserted = amostra_client.create(**req_dict)
    retrieved = next(amostra_client.find(foo="bar"))
    assert retrieved["uid"] == inserted


def test_update_request(amostra_server, amostra_client):
    amostra_client = RequestReference(
        host=TESTING_CONFIG["host"], port=TESTING_CONFIG["port"]
    )
    m_uid = str(uuid4())
    req_dict = dict(
        sample="hidefix",
        time=time.time(),
        uid=m_uid,
        state="active",
        seq_num=0,
        foo="bar",
        hero="obelix",
        antihero="romans",
    )
    amostra_client.create(**req_dict)
    amostra_client.update(query={"uid": m_uid}, update={"state": "inactive"})
    updated_req = next(amostra_client.find(uid=m_uid))
    assert updated_req["state"] == "inactive"
