import jsonschema
import json
from doct import Document
from uuid import uuid4


def look_up_schema(schema):
    raise NotImplemented()


class SampleReference:
    """Reference implementation of generic sample manager

    For simplicity, built on top of a list of dicts.

    This is primarily a reference implementation / for testing but can be
    used in production for very small numbers of samples.

    """
    def __init__(self, sample_dict=None):
        if sample_dict is None:
            sample_dict = []
        self._sample_list = [dict(d) for d in sample_dict]
        ln = len(self._sample_list)
        if ln != len(set(d['name'] for d in self._sample_list)):
            raise ValueError("duplicate names")
        if ln != len(set(d['uid'] for d in self._sample_list)):
            raise ValueError("duplicate uids")

    def add(self, name, schema=None, **kwargs):
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
        doc = {'uid': uid, 'name': name, **kwargs}
        if schema is not None:
            doc['schema'] = schema
            schema = look_up_schema(schema)
            jsonschema.validate(doc, schema)

        self._sample_list.append(doc)
        return uid

    def update(self, uid, overwrite=True, **kwargs):
        """Update an existing sample in place.

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

        old, = [d for d in self._sample_list if d['uid'] == uid]

        if not overwrite:
            if set(old) ^ set(kwargs):
                raise ValueError("overlapping keys")
        old, new = dict(old), old
        new.update(**kwargs)
        return Document('sample', old), Document('sample', new)

    def find(self, **kwargs):
        """Find samples by keys

        Yields all documents which have all of the keys equal
        to the kwargs.  ex ::

            for k, v in kwargs:
                assert d[k] == v

        for all `d` yielded.

        No kwargs yields matches all samples.

        Yields
        ------
        doc : doct.Document
            Documents which have all keys with the given values

        """
        for d in self._sample_list:
            for k, v in kwargs.items():
                if k not in d or d[k] != v:
                    break
            else:
                yield Document('sample', d)

    def find_raw_mongo(self, mongo_query):
        raise NotImplemented()

    def dump_to_json(self, fpath):
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                json.dump(self._sample_list, fout)
        else:
            json.dump(self._sample_list, fpath)

    def dump_to_yaml(self, fpath):
        import yaml
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                yaml.dump(self._sample_list, fout)
        else:
            yaml.dump(self._sample_list, fpath)
