from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from doct import Document
import ujson
from uuid import uuid4
import requests
import time as ttime
from amostra.client import conf
from os.path import expanduser
import mongoquery

# TODO: Separate local and online commands.py
# TODO: Replace get, post, put and exception handling with _ from utils


class AmostraException(Exception):
    pass

class _get():
    pass

class _post():
    pass

class _put():
    pass

class SampleReference(object):
    """Reference implementation of generic sample manager"""
    def __init__(self, host=conf.conn_config['host'],
                 port=conf.conn_config['port']):
        """Constructor. 

        Parameters
        ----------
        host: str, optional
            Machine name/address for amostra server
        port: int, optional
            Port amostra server is initiated on
        """
        self.host = host
        self.port = port

    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)
    
    @property
    def _samp_url(self):
        return self._server_path + 'sample'
            
    def create(self, name=None, time=None, uid=None, container=None,
               **kwargs):
        """Insert a sample to the database

        Parameters
        ----------
        name : str
            The name of the sample.  This must be unique in the database
        time: float
            The time sample is created. Client provided timestamp
        uid: str
            Unique identifier for a sample document
        container: str, list
            A single or a list of container documents or uids

        Returns
        -------
        uid : str, list
            uid of the inserted document
        """
        doc = dict(uid=uid if uid else str(uuid4()),
                   name=name, time=time if time else ttime.time(),
                   container=container if container else 'NULL',
                   **kwargs)
        domt = ujson.dumps(doc)
        r = requests.post(self._samp_url,
                          data=domt)
        r.raise_for_status()
        return doc[uid]

    def create_sample_list(self, sample_list):
        """Insert a sample to the database

        Parameters
        ----------
        sample_list : list
            List of dictionaries


        Returns
        -------
        uid : str, list
            uid of the inserted document
        """
        uid_list = []
        for doc in sample_list:
            try:
                uid_list.append(doc['uid'])
            except KeyError:
                raise AmostraException('Every sample must have a uid')
            domt = ujson.dumps(doc)
            r = requests.post(self._samp_url,
                              data=domt)
            r.raise_for_status()

    def update(self, query, update):
        """Update a request given a query and name value pair to be updated. No upsert support.
        For more info on upsert, check Mongo documentations
        
        Parameters
        -----------
        query: dict
            Allows finding Sample documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        """
        payload = dict(query=query, update=update)
        r = requests.put(url=self._samp_url,
                         data=ujson.dumps(payload))
        r.raise_for_status()
        return True
        
    def find(self, as_document=False, **kwargs):
        """
        Parameters
        ----------
        as_document: bool
            Yields doct.Document if True

        Yields
        ------
        c : dict, doct.Document
            Documents which have all keys with the given values
        """
        r = requests.get(self._samp_url,
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        if as_document:        
            for c in content:
                yield Document('Sample', c)
        else:
            for c in content:
                yield c
            
    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path + 'schema', params=ujson.dumps('sample'))
        r.raise_for_status()
        return ujson.loads(r.text)


class RequestReference(object):
    """Reference implementation of generic request"""
    def __init__(self, host=conf.conn_config['host'], port=conf.conn_config['port']):
        """Constructor

        Parameters
        ----------
        host: str, optional
            Machine name/address for amostra server
        port: int, optional
            Port amostra server is initiated on
        """
        self.host = host
        self.port = port
                    
    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)

    @property
    def _req_url(self):
        return self._server_path + 'request'
    
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
        r = requests.post(url=self._req_url,
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""
        r = requests.get(self._req_url,
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        if as_document:        
            for c in content:
                yield Document('Request', c)
        else:
            for c in content:
                yield c
                
    def update(self, query, update):
        """Update a request given a query and name value pair to be updated.
        No upsert(s).
        
        Parameters
        -----------
        query: dict
            Allows finding Request documents to be updated.
        update: dict
            Name/value pair that is to be replaced within an existing Request doc.
        """
        payload = dict(query=query, update=update)
        r = requests.put(url=self._req_url,
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
    def __init__(self, host=conf.conn_config['host'], port=conf.conn_config['port']):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self.port = port
        self.host = host

    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)

    @property
    def _cont_url(self):
        return self._server_path + 'container'

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
        r = requests.post(url=self._cont_url,
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""
        r = requests.get(self._cont_url,
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
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
        r = requests.put(url=self._cont_url,
                         data=ujson.dumps(payload))
        r.raise_for_status()

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        'schema', params=ujson.dumps('container'))
        r.raise_for_status()
        return ujson.loads(r.text)


def _find_local(fname, qparams):
    """Update a document created using the local framework
    Parameters
    -----------
    fname: str
        Name of the query should be run
    qparams: dict
        Query parameters. Similar to online query methods

    Yields
    ------------
    c: doct.Document, StopIteration
        Result of the query if found

    """
    res_list = []
    try:
        with open(fname, 'r') as fp:
            local_payload = ujson.load(fp)
        qobj = mongoquery.Query(qparams)
        for _sample in local_payload:
            try:
                qobj.match(_sample)
                res_list.append(_sample)
            except mongoquery.QueryError:
                # this document is not it, skip it
                pass
    except FileNotFoundError:
        raise RuntimeWarning('Local file {} does not exist'.format(fname))
    for c in res_list:
        yield c


def _update_local(fname, qparams, replacement):
    try:
        with open(fname, 'r') as fp:
            local_payload = ujson.load(fp)
        qobj = mongoquery.Query(qparams)
        for _sample in local_payload:
            try:
                qobj.match(_sample)
                for k, v in replacement.iteritems():
                    _sample[key] = v
            except mongoquery.QueryError:
                pass
        with open(fname, 'w') as fp:
            fp.write(ujson.dump(local_payload))
    except FileNotFoundError:
        raise RuntimeWarning('Local file {} does not exist'.format(fname))


class LocalSampleReference:
    """Handle sample information locally via json files"""
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
        
    def create(self, name=None, time=None, uid=None, container=None,
               **kwargs):
        payload = dict(uid=uid if uid else str(uuid4()),
                       name=name, time=time if time else ttime.time(),
                       container=container if container else 'NULL',
                       **kwargs)
        self.sample_list.append(payload)
        with open(self._samp_fname, 'w+') as fp:
            ujson.dump(self.sample_list, fp)
        return payload
        
    @property
    def _samp_fname(self):
        return expanduser(self.top_dir + '/samples.json')

    def update(self, query, replacement):
        _update_local(self._samp_fname, query, replacement)

    def find(self, **kwargs):
        return _find_local(self._samp_fname, kwargs)


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
                             time=time if time else ttime.time(), state=state,
                             seq_num=seq_num, **kwargs)
        self.request_list.append(local_payload)
        with open(self._req_fname, 'w+') as fp:
            ujson.dump(self.request_list, fp)
    
    def update(self, query, replacement):
        _update_local(self._req_fname, query, replacement)


    def find(self, **kwargs):
        return _find_local(self._req_fname, kwargs)


class LocalContainerReference:
    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir
        try:        
            with open(self._cont_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        self.container_list = tmp if tmp else []
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

    def update(self, query, replacement):
        _update_local(self._cont_fname, query, replacement)

    def find(self, **kwargs):
        return _find_local(self._cont_fname, kwargs)