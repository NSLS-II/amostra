from doct import Document
import ujson
from uuid import uuid4
import requests
import time
from amostra.client import conf


class SampleReference(object):
    """Reference implementation of generic sample manager"""
    def __init__(self, sample_list=[], host=conf.conn_config['host'],
                 port=conf.conn_config['port']):
        """Constructor. 

        Parameters
        ----------
        sample_list: list
            List of desired sample(s) to be created
        host: str
            Machine name/address for tornado instance
        port: int
            Port tornado server runs on
        """
        self.host = host
        self.port = port        
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
#        The sample_list here holds all samples created by
#        this SampleReference client. It is useful for a single shot session but
#        I am fine if you guys want to drop it.         
        if sample_list is None:
            sample_list = []
        if not isinstance(sample_list, list):
            raise TypeError('Not a correct type for the constructor.Expects list')
        self._sample_list = [dict(d) for d in sample_list]
        ln = len(self._sample_list)
        if ln != len(set(d['name'] for d in self._sample_list)):
            raise ValueError("duplicate names")
        if ln != len(set(d['uid'] for d in self._sample_list)):
            raise ValueError("duplicate uids")
        if sample_list:
            # if there is a list in mind, create it
            domt = ujson.dumps(self._sample_list)
            r = requests.post(self._server_path + 'sample',
                              data=domt)
            r.raise_for_status()

    def create(self, name, time=time.time(), uid=None,
               **kwargs):
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
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        if any(d['name'] == name for d in self._sample_list):
            raise ValueError(
                "document with name {} already exists".format(name))
        if uid is None:
            uid = str(uuid4())
        doc = dict(uid=uid, name=name, time=time, 
                   **kwargs)
        domt = ujson.dumps(doc)
        r = requests.post(self._server_path + 'sample',
                          data=domt)
        r.raise_for_status()
        self._sample_list.append(doc)
        return doc

    def update(self, query, update, host=conf.conn_config['host'], 
             port=conf.conn_config['port']):
        """Update a request given a query and name value pair to be updated.
        No upsert(s). If doc does not exist, simply do not update
        
        Parameters
        -----------
        query: dict
            Allows finding Sample documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        host: str
            Backend machine id to be connected. Not mongo, tornado
        port: int
            Backend port id. Again, tornado, not mongo daemon
        """
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        payload = dict(query=query, update=update)
        r = requests.put(url=self._server_path + 'sample',
                         data=ujson.dumps(payload))
        r.raise_for_status()
        
    def find(self, as_document=False, **kwargs):
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
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        r = requests.get(self._server_path + 'sample',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._sample_list.extend(content)
        if as_document:        
            for c in content:
                yield Document('sample', c)
        else:
            for c in content:
                yield c
            
    def dump_to_json(self, fpath):
        # Seems done
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                ujson.dump(self._sample_list, fout)
        else:
            ujson.dump(self._sample_list, fpath)

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


class RequestReference(object):
    """Reference implementation of generic request

    For simplicity, built on top of a list of dicts.

    """
    def __init__(self, host=conf.conn_config['host'], port=conf.conn_config['port'],
                 sample=None, time=time.time(), uid=str(uuid4()), state='active',
                 seq_num=0, **kwargs):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self.host = host
        self.port = port
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        self._request_list = []
        if sample:
            payload = dict(uid=uid, sample=sample['uid'], time=time,state=state,
                           seq_num=seq_num, **kwargs)
            r = requests.post(self._server_path + 'request',
                            data=ujson.dumps(payload))
            r.raise_for_status()
            self._request_list.append(payload)

    def create(self, sample=None, time=time.time(),
               uid=None, state='active', seq_num=0, **kwargs):
        """ Create a sample entry in the dataase
        Parameters
        ----------
        sample: dict, doct.Document, optional
            The sample this reference refers to
        time: float
            Time request got created
        uid: str
            Unique identifier for
        state: str
            Enum 'active' or 'inactive' that displays the state of a request    
        seq_num: int
            Sequence number for creation of the request. Not indexed but can be updated

        Returns
        -------
        payload['uid']
            uid of the payload created
        """
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        payload = dict(uid=uid if uid else str(uuid4()), 
                       sample=sample['uid'] if sample else 'NULL',
                       time=time,state=state,
                       seq_num=seq_num, **kwargs)
        r = requests.post(url=self._server_path + 'request',
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""
        self._server_path = 'http://{}:{}/' .format(self.host, self.port) 
        r = requests.get(self._server_path + 'request',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._request_list.extend(content)
        if as_document:        
            for c in content:
                yield Document('request', c)
        else:
            for c in content:
                yield c
                
    def update(self, query, update):
        """Update a request given a query and name value pair to be updated.
        No upsert(s). If doc does not exist, simply do not update
        
        Parameters
        -----------
        query: dict
            Allows finding Request documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        host: str
            Backend machine id to be connected. Not mongo, tornado
        port: int
            Backend port id. Again, tornado, not mongo daemon
        """
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        payload = dict(query=query, update=update)
        r = requests.put(url=self._server_path + 'request',
                         data=ujson.dumps(payload))
        r.raise_for_status()
        

class ContainerReference(object):
    """Reference implementation of generic container"""
    def __init__(self, host=conf.conn_config['host'], port=conf.conn_config['port'],
                 **kwargs):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self.port = port
        self.host = host
        self._server_path = 'http://{}:{}/' .format(host, port)
        self._request_list = []
        if kwargs:
            r = requests.post(self._server_path + 'container',
                            data=ujson.dumps(kwargs))
            r.raise_for_status()
            self._request_list.append(kwargs)
    
    def create(self, uid=None, time=time.time(), **kwargs):
        """    
        Returns
        -------
        payload['uid']
            uid of the payload created
        """
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        if uid is None:
            uid = str(uuid4())        
        payload = dict(uid=uid, time=time, **kwargs)
        r = requests.post(url=self._server_path + 'container',
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload['uid']
    
    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)        
        r = requests.get(self._server_path + 'container',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._request_list.extend(content)
        if as_document:
            for c in content:
                yield Document('container', c)
        else:
            for c in content:
                yield c
    
    def update(self, query, update):
        """Update a request given a query and name value pair to be updated.
        No upsert(s). If doc does not exist, simply do not update
        
        Parameters
        -----------
        query: dict
            Allows finding Container documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        host: str
            Backend machine id to be connected. Not mongo, tornado
        port: int
            Backend port id. Again, tornado, not mongo daemon
        """
        self._server_path = 'http://{}:{}/' .format(self.host, self.port)
        payload = dict(query=query, update=update)
        r = requests.put(url=self._server_path + 'container',
                         data=ujson.dumps(payload))
        r.raise_for_status()