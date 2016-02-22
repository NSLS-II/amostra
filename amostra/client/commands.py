from doct import Document
import ujson
from uuid import uuid4
import requests
import time


class SampleReference:
    """Reference implementation of generic sample manager
    This is primarily a reference implementation / for testing but can be
    used in production for very small numbers of samples.

    """
    def __init__(self, sample_dict=None, host, port):
        self._server_path = 'http://{}:{}/' .format(host, port)
        if sample_dict is None:
            sample_dict = []
        self._sample_list = [dict(d) for d in sample_dict]
        ln = len(self._sample_list)
        if ln != len(set(d['name'] for d in self._sample_list)):
            raise ValueError("duplicate names")
        if ln != len(set(d['uid'] for d in self._sample_list)):
            raise ValueError("duplicate uids")

    def add(self, name, time=time.time(), **kwargs):
        """Add a sample to the database
        All kwargs are collected and passed through to the documents

        Parameters
        ----------
        name : str
            The name of the sample.  This must be unique in the database

        schema : str, optional
             The schema used to validate the kwargs prior to inserting
             into the database.  The schema must allow for 'uid',
             'schema', and 'name' string fields.

        Returns
        -------
        uid : str
            uid of the inserted document.
        """
        if any(d['name'] == name for d in self._sample_list):
            raise ValueError(
                "document with name {} already exists".format(name))
        uid = str(uuid4())
        doc = dict(uid=uid, name=name, **kwargs)
        # let is serialize first. If it fails, do not add to list
        domt = ujson.dumps(doc)
        self._sample_list.append(doc)
        r = requests.post(self._server_path + '/sample',
                          data=domt)
        r.raise_for_status()
        return uid

    def create_index(self, fields):
        raise NotImplementedError('I do not think this is a good idea')

    def update(self, uid, overwrite=True, **kwargs):
        """Update an existing Sample
            raise ValueError("Can not change sample name")
        old, = [d for d in self._sample_list if d['uid'] == uid]

        if not overwrite:
            if set(old) ^ set(kwargs):
                raise ValueError("overlapping keys")sting sample in place.

        kwargs are merged into the existing sample document

        Parameters
        ----------
        uid : str
            Unique id for the sample.

        overwrite : bool, optional
            If true the upddate

        Returns
        -------
        old, new : doct.Document
            The old and new documents
        """
        if 'name' in kwargs:
            raise ValueError("Can not change sample name")
        old, new = dict(old), old
        new.update(**kwargs)
        return Document('sample', old), Document('sample', new)

    def find(self, **kwargs):
        """Find samples by keys
        First iterates over samples created by this instance,
        if sample not found, makes the trip to the server.
        Yields all documents which have all of the keys equal
        to the kwargs.  ex ::

            for k, v in kwargs:
                assert d[k] == v

        for all `d` yielded.

        No kwargs yields matches all samples.

        Yields
        ------
        c : dict
            Documents which have all keys with the given values

        """
        r = requests.get(self._server_path +
                        '/sample',
                        params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._sample_list.extend(content)
        for c in content:
            yield Document('sample', c)

    def find_raw_mongo(self, mongo_query, json=False):
        """Return raw dicts or json instead of doct"""
        r = requests.get(self._server_path +
                        '/sample',
                        params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._sample_list.extend(content)
        for c in content:
            yield c

    def dump_to_json(self, fpath):
        # Seems done
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                json.dump(self._sample_list, fout)
        else:
            json.dump(self._sample_list, fpath)

    def dump_to_yaml(self, fpath):
        """For those who don't want to write into the database or work offline."""
        import yaml
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                yaml.dump(self._sample_list, fout)
        else:
            yaml.dump(self._sample_list, fpath)

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        '/schema_ref', params=ujson.dumps('sample'))
        r.raise_for_status()
        return ujson.loads(r.text)

    def get_requests(self):
        """Get all active requests given a sample"""
        raise NotImplementedError('In theaters Spring 2016')


class RequestReference:
    """Reference implementation of generic request

    For simplicity, built on top of a list of dicts.

    """
    def __init__(self, sample):
        """Handles connection configuration to the service backend."""
        self.sample_uid = sample.uid
        self._request_url = sample._sample_path + '/request'
        
    def create_request(self, **kwargs):
        r = requests.post(url=self._request_url, 
                          data=ujson.dumps(kwargs))
        r.raise_for_status()
    
    def find_request(self, sort_by=None, **kwargs):
        raise NotImplementedError('In theaters Spring 2016')
    
    def update_request(self, **kwargs):
        pass