from doct import Document
import time as ttime
import pytest
from ..client.api import AmostraClient
from requests.exceptions import HTTPError, RequestException
from .conftest import testing_config

import uuid


def test_client_constructor(astore_client):
    pytest.raises(TypeError, AmostraClient)


def test_connection_switch(astore_client):
    astore_client.host = "caesar"
    pytest.raises(RequestException, astore_client.create_sample, "asterix")
    astore_client.host = testing_config["host"]


def test_sample_create(astore_server, astore_client):
    r1 = astore_client.create_sample(name="test1")
    r2 = astore_client.create_sample(name="test2", uid=str(uuid.uuid4()))
    m_kwargs = dict(owner="test", level="inferno", type="automated", material="CoFeB")
    r3 = astore_client.create_sample(name="test3", uid=str(uuid.uuid4()), **m_kwargs)


def test_duplicate_sample(astore_client):
    _com_uid = str(uuid.uuid4())
    astore_client.create_sample(name="test_sample", uid=_com_uid, custom=False)
    pytest.raises(
        HTTPError, astore_client.create_sample, name="test_duplicate", uid=_com_uid
    )


def test_invalid_sample(astore_client):
    pytest.raises(TypeError, astore_client.create_sample)


def test_find_sample(astore_client):
    m_sample = dict(
        name="comp_samp",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="test",
        project="ci-tests",
        beamline_id="test-ci",
    )
    s = astore_client.create_sample(**m_sample)
    s_ret = astore_client.find_sample(uid=m_sample["uid"])
    assert s_ret[0]["uid"] == m_sample["uid"]


def test_find_sample_as_doc(astore_client):
    m_sample = dict(
        name="comp_sam",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="arkilic",
        project="trial",
        beamline_id="trial_b",
        container="legion1",
    )
    astore_client.create_sample(**m_sample)
    s_ret = astore_client.find_sample(uid=m_sample["uid"], as_document=True)
    assert s_ret[0] == Document("Sample", m_sample)


def test_update_sample(astore_server, astore_client):
    test_sample = dict(
        name="up_sam",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="arkilic",
        project="trial",
        beamline_id="trial_b",
        state="active",
        container="legion2",
    )
    astore_client.create_sample(**test_sample)
    astore_client.update_sample(
        query={"uid": test_sample["uid"]},
        update={"state": "inactive", "time": ttime.time()},
    )
    updated_samp = astore_client.find_sample(name="up_sam")[0]
    assert updated_samp["state"] == "inactive"


def test_update_sample_illegal(astore_client):
    test_sample = dict(
        name="up_sam",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="arkilic",
        project="trial",
        beamline_id="trial_b",
        updated=False,
    )
    pytest.raises(
        HTTPError,
        astore_client.update_sample,
        query={"name": test_sample["name"]},
        update={"uid": "illegal"},
    )


def test_container_create(astore_client):
    ast_cont = {
        "name": "obelix",
        "dog": "hidefix",
        "time": ttime.time(),
        "container": "gauls",
        "uid": str(uuid.uuid4()),
    }
    cont1 = astore_client.create_container(**ast_cont)
    assert cont1 == ast_cont["uid"]


def test_find_container(astore_client):
    f_cont = dict(
        name="comp_sam",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="hidefix",
        project="ceasar",
        container="gauls",
        beamline_id="fiction",
    )
    c_uid = astore_client.create_container(**f_cont)
    c_ret_doc = astore_client.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc["uid"] == c_uid


def test_find_container_as_doc(astore_client):
    f_cont = dict(
        name="comp_sam",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="hidefix",
        project="ceasar",
        container="gauls",
        beamline_id="fiction",
    )
    c_uid = astore_client.create_container(**f_cont)
    c_ret_doc = astore_client.find_container(uid=c_uid, as_document=True)[0]
    assert Document == type(c_ret_doc)
    assert c_ret_doc["uid"] == c_uid


def test_update_container(astore_client):
    orig_cont = dict(
        name="obelix",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="chief",
        project="egypt",
        beamline_id="fiction",
        state="active",
        container="SPQR",
    )
    m_uid = astore_client.create_container(**orig_cont)
    astore_client.update_container(
        query={"uid": orig_cont["uid"]},
        update={"state": "inactive", "time": ttime.time()},
    )
    updated_cont = astore_client.find_container(uid=m_uid)[0]
    assert updated_cont["state"] == "inactive"


def test_update_container_illegal(astore_client):
    orig_cont = dict(
        name="obelix",
        uid=str(uuid.uuid4()),
        time=ttime.time(),
        owner="chief",
        project="egypt",
        beamline_id="fiction",
        state="active",
        container="SPQR",
    )
    m_uid = astore_client.create_container(**orig_cont)
    test_time = ttime.time()
    pytest.raises(
        HTTPError,
        astore_client.update_container,
        query={"uid": orig_cont["uid"]},
        update={"uid": str(uuid.uuid4())},
    )


def test_request_create(astore_client):
    astore_client.create_request(
        sample="roman_sample",
        time=ttime.time(),
        uid=None,
        state="active",
        seq_num=0,
        foo="bar",
        hero="asterix",
        antihero="romans",
    )


def test_duplicate_request(astore_client):
    m_uid = str(uuid.uuid4())
    astore_client.create_request(
        sample="hidefix",
        time=ttime.time(),
        uid=m_uid,
        state="active",
        seq_num=0,
        foo="bar",
        hero="asterix",
        antihero="romans",
    )
    pytest.raises(
        HTTPError,
        astore_client.create_request,
        sample="hidefix",
        time=ttime.time(),
        uid=m_uid,
        state="active",
        seq_num=0,
        foo="bar",
        hero="asterix",
        antihero="romans",
    )


def test_request_find(astore_client):
    req_dict = dict(
        sample="hidefix",
        time=ttime.time(),
        uid=str(uuid.uuid4()),
        state="active",
        seq_num=0,
        foo="bar",
        hero="obelix",
        antihero="romans",
    )
    inserted = astore_client.create_request(**req_dict)
    retrieved = astore_client.find_request(uid=inserted)[0]
    assert retrieved["uid"] == inserted


def test_update_request(astore_client):
    m_uid = str(uuid.uuid4())
    req_dict = dict(
        uid=m_uid,
        sample="hidefix",
        time=ttime.time(),
        seq_num=0,
        foo="bar",
        hero="obelix",
        antihero="romans",
    )
    astore_client.create_request(**req_dict)
    astore_client.update_request(query={"uid": m_uid}, update={"state": "inactive"})
    updated_req = astore_client.find_request(uid=m_uid)[0]
    assert updated_req["state"] == "inactive"
