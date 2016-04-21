from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from doct import Document
import ujson
from uuid import uuid4
import requests
import time as ttime
from amostra.client import conf


# TODO: Go over local lists prior to file lookups in local version
# TODO: Make use of local lists for all collections
# TODO: Add tests for both local and online commands/clients
# TODO: Add AmostraClient as a convenient way to interact with commands.py

class AmostraException(Exception):
    pass


def _get(url, params):
    r = requests.get(url, ujson.dumps(params))
    r.raise_for_status()
    return ujson.loads(r.text)


def _post(url, data):
    r = requests.post(url,
                      data=ujson.dumps(data))
    r.raise_for_status()


def _put(url, query, update):
    update_cont = {'query': query, 'update': update}
    r = requests.put(url,
                     data=ujson.dumps(update_cont))
    r.raise_for_status()


class SampleReference(object):
    """Reference implementation of generic sample manager"""
    def __init__(self, host=conf.conn_config['host'],
                 port=conf.conn_config['port']):
        """Constructor. 

        Parameters
        ----------
        host: str, optional
            Machine name/address for Amostra server
        port: int, optional
            Port Amostra server is initiated on
        """
        self.host = host
        self.port = port

    @property
    def _server_path(self):
        return 'http://{}:{}/' .format(self.host, self.port)
    
    @property
    def _samp_url(self):
        return self._server_path + 'sample'
            
    def create(self, name, time=None, uid=None, container=None,
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
        _post(self._samp_url, doc)
        return doc

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
        _put(self._samp_url, query, update)
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
        content = _get(self._samp_url, params=kwargs)
        if as_document:
            for c in content:
                yield Document('Sample', c)
        else:
            for c in content:
                yield c
            
    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path + 'schema',
                         params=ujson.dumps('sample'))
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
        _post(self._req_url, payload)
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator"""
        content = _get(self._req_url, kwargs)
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
        _put(self._req_url, query, update)
        return True

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
        _post(self._cont_url, payload)
        return payload

    def find(self, as_document=False, **kwargs):
        """Given a set of MongoDB search parameters, return a requests iterator"""
        content = _get(self._cont_url, kwargs)
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
        _put(self._cont_url, query, update)
        return True

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        'schema', params=ujson.dumps('container'))
        r.raise_for_status()
        return ujson.loads(r.text)