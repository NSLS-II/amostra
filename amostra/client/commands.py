from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from doct import Document
import ujson
from uuid import uuid4
import requests
import time as ttime
from amostra.client import conf
from os.path import expanduser 

class SampleReference(object):
    """Reference implementation of generic sample manager"""
    def __init__(self, sample_list=[], host=conf.conn_config['host'],
                 port=conf.conn_config['port']):
        """Constructor. 

        Parameters
        ----------
        sample_list: list, optional
            List of desired sample(s) to be created
        host: str, optional
            Machine name/address for tornado instance
        port: int, optional
            Port tornado server runs on
        """
        self.host = host
        self.port = port
        if not isinstance(sample_list, list):
            raise TypeError("sample_list must be a list")
        if not isinstance(sample_list, list):
            raise TypeError('Not a correct type for the constructor.Expects list')
        self._sample_list = [dict(d) for d in sample_list]
        ln = len(self._sample_list)
        if ln != len(set(d['name'] for d in self._sample_list)):
            raise ValueError("duplicate names")
        if ln != len(set(d['uid'] for d in self._sample_list)):
            raise ValueError("duplicate uids")
        if sample_list:
            domt = ujson.dumps(self._sample_list)
            r = requests.post(self._server_path + 'sample',
                              data=domt)
            r.raise_for_status()

    @property
    def host(self):
        return self.__host
    
    @host.setter
    def host(self, new_host):
        self.__host = new_host
     
    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, new_port):
        self.__port = new_port   
        
    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)
    
            
    def create(self, name=None, time=None, uid=None, container=None,
               **kwargs):
        """Add a sample to the database
        All kwargs are collected and passed through to the documents
        In order to modify which tornao server this routine talks to,
        simply set self.host and self.port to the correct host and port.
        Do not mess with _server_path variable alone.
        
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
        doc = dict(uid=uid if uid else str(uuid4()),
                   name=name, time=time if time else ttime.time(),
                   container=container if container else 'NULL',
                   **kwargs)
        domt = ujson.dumps(doc)
        r = requests.post(self._server_path + 'sample',
                          data=domt)
        r.raise_for_status()
        self._sample_list.append(doc)
        return doc

    def update(self, query, update):
        """Update a request given a query and name value pair to be updated.
        No upsert(s). If doc does not exist, simply do not update
        In order to modify which tornao server this routine talks to,
        simply set self.host and self.port to the correct host and port.
        Do not mess with _server_path variable.
        
        Parameters
        -----------
        query: dict
            Allows finding Sample documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        """
        payload = dict(query=query, update=update)
        r = requests.put(url=self._server_path + 'sample',
                         data=ujson.dumps(payload))
        r.raise_for_status()
        return True
        
    def find(self, as_document=False, as_json=False, **kwargs):
        """
        Parameters
        ----------
        
        as_document: bool
            Return doct.Document if True else return a dict

        Yields
        ------
        c : dict
            Documents which have all keys with the given values

        """
        r = requests.get(self._server_path + 'sample',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        self._sample_list.extend(content)
        if as_json:
            return r.text
        if as_document:        
            for c in content:
                yield Document('Sample', c)
        else:
            for c in content:
                yield c
            
    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        'schema', params=ujson.dumps('sample'))
        r.raise_for_status()
        return ujson.loads(r.text)


class RequestReference(object):
    """Reference implementation of generic request

    For simplicity, built on top of a list of dicts.

    """
    def __init__(self, host=conf.conn_config['host'], port=conf.conn_config['port'],
                 sample=None, time=None, uid=None, state='active',
                 seq_num=0, **kwargs):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self.host = host
        self.port = port
        self._request_list = []
        if sample:
            payload = dict(uid=uid if uid else str(uuid4()),
                           sample=sample['uid'] if sample else 'NULL',
                           time=time if time else ttime.time(), state=state,
                           seq_num=seq_num, **kwargs)
            r = requests.post(self._server_path + 'request', data=ujson.dumps(payload))
            r.raise_for_status()
            self._request_list.append(payload)
            
    @property
    def host(self):
        return self.__host
    
    @host.setter
    def host(self, new_host):
        self.__host = new_host
     
    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, new_port):
        self.__port = new_port   
        
    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)
    
    
    def create(self, sample=None, time=None,
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
        payload = dict(uid=uid if uid else str(uuid4()), 
                       sample=sample['uid'] if sample else 'NULL',
                       time=time if time else ttime.time(),state=state,
                       seq_num=seq_num, **kwargs)
        r = requests.post(url=self._server_path + 'request',
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator""" 
        r = requests.get(self._server_path + 'request',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._request_list.extend(content)
        if as_document:        
            for c in content:
                yield Document('Request', c)
        else:
            for c in content:
                yield c
                
    def update(self, query, update):
        """Update a request given a query and name value pair to be updated.
        No upsert(s). If doc does not exist, simply do not update
        
        Parameters
        -----------
        query: dict
            Allows finding Request documents to be updated.
        update: dict
            Name/value pair that is to be replaced within an existing Request doc.
        """
        payload = dict(query=query, update=update)
        r = requests.put(url=self._server_path + 'request',
                         data=ujson.dumps(payload))
        r.raise_for_status()

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        'schema', params=ujson.dumps('request'))
        r.raise_for_status()
        return ujson.loads(r.text)


class ContainerReference(object):
    """Reference implementation of generic container"""
    def __init__(self, uid=None, time=None, host=conf.conn_config['host'], port=conf.conn_config['port'],
                 **kwargs):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self._container_list = []
        self.port = port
        self.host = host
        if kwargs:        
            _cont_dict = dict(uid=uid if uid else str(uuid4()), 
                              time=time if time else ttime.time(),
                              **kwargs)        
            r = requests.post(self._server_path + 'container',
                            data=ujson.dumps(_cont_dict))
            r.raise_for_status()
            self._container_list.append(_cont_dict)
    
    @property
    def host(self):
        return self.__host
    
    @host.setter
    def host(self, new_host):
        self.__host = new_host
     
    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, new_port):
        self.__port = new_port   
        
    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)
    
    def create(self, uid=None, time=None, **kwargs):
        """Insert a container document. Schema validation done
        on the server side. No native Python object (e.g. np.ndarray)
        due to performance constraints. 
        
        Parameters
        ----------
        uid: str
            Unique identifier for a Container document
        time: float
            Time document created. Client side timestamp
      
        Returns
        -------
        payload['uid']
            uid of the payload created
        """        
        payload = dict(uid=uid if uid else str(uuid4()),
                       time=time if time else ttime.time(), **kwargs)
        r = requests.post(url=self._server_path + 'container',
                          data=ujson.dumps(payload))
        r.raise_for_status()
        self._container_list.append(payload)        
        return payload
    
    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""        
        r = requests.get(self._server_path + 'container',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        self._container_list.extend(content)
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
            Allows finding Container documents to be updated.
        update: dict
            Name/value pair that is to be replaced within an existing Request doc.
        """
        payload = dict(query=dict(query), update=update)
        r = requests.put(url=self._server_path + 'container',
                         data=ujson.dumps(payload))
        r.raise_for_status()

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        'schema', params=ujson.dumps('container'))
        r.raise_for_status()
        return ujson.loads(r.text)


class LocalSampleReference:

    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir
        try:        
            with open(self._samp_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        try:
            self.sample_list = tmp if tmp else []
        except FileNotFoundError:
            self.sample_list = []
        # TODO: Replicate sample_list behavior in the constructor
        
    def create(self,name=None, time=None, uid=None, container=None,
               **kwargs):
        payload = dict(uid=uid if uid else str(uuid4()),
                   name=name, time=time if time else ttime.time(),
                   container=container if container else 'NULL',
                   **kwargs)
        self.sample_list.append(payload)
        with open(self._samp_fname, 'w+') as fp:
            ujson.dump(self.sample_list, fp)
        return payload
    
    def update(self):
        with open(self._samp_fname, 'a+') as fp:
            local_payload = ujson.load(fp)

    def find(self):
        with open(self._samp_fname, 'r') as fp:
            print(fp)
            local_payload = ujson.load(fp)
        print(local_payload, type(local_payload))
        
    @property
    def _samp_fname(self):
        return  expanduser(self.top_dir + '/samples.json')
    
class LocalRequestReference:
    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir        
        try:        
            with open(self._req_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        try:
            self.request_list = tmp if tmp else []
        except FileNotFoundError:
            self.request_list = []
    
    @property
    def _req_fname(self):
        return expanduser(self.top_dir + '/requests.json')
    
    def create(self, sample=None, time=None, uid=None, state='active', 
               seq_num=0, **kwargs):        
        local_payload = dict(uid=uid if uid else str(uuid4()), 
                       sample=sample['uid'] if sample else 'NULL',
                       time=time if time else ttime.time(),state=state,
                       seq_num=seq_num, **kwargs)
        self.request_list.append(local_payload)
        with open(self._req_fname, 'w+') as fp:
            ujson.dump(self.request_list, fp)
    
    def update(self):
        with open(self._req_fname,'r+') as fp:
            local_payload = ujson.load(fp)

    def find(self):
        with open(self._req_fname,'r') as fp:
            local_payload = ujson.load(fp)
        print(local_payload)
        

class LocalContainerReference:
    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir
        try:        
            with open(self._cont_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        try:
            self.container_list = tmp if tmp else []
        except FileNotFoundError:
            self.container_list = []        
        
    @property
    def _cont_fname(self):
        return expanduser(self.top_dir + '/containers.json')

    
    def create(self, uid=None, time=None, **kwargs):        
        payload = dict(uid=uid if uid else str(uuid4()),
                       time=time if time else ttime.time(), **kwargs)
        self.container_list.append(payload)
        with open(self._cont_fname, 'w+') as fp:
            ujson.dump(self.container_list, fp)
    
    def update(self):
        with open(self._cont_fname,'r+') as fp:
            local_payload = ujson.load(fp)

    def find(self):
        with open(self._cont_fname,'r') as fp:
            local_payload = ujson.load(fp)
        print(local_payload)