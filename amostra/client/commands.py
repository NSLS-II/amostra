from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from doct import Document
import ujson
from uuid import uuid4
import requests
import time as ttime
from ..client import conf
from .amutils import doc_or_uid_to_uid

# TODO: Add tests for both local and online commands/clients
# TODO: Add AmostraClient as a convenient way to interact with commands.py

class AmostraException(Exception):
    pass


def _get(url, params):
    """RESTful API get (querying)

    Parameters
    ----------
    url: str
        Address for the amostra server
    params: dict
        Query parameters to be sent to mongo instance

    Returns
    -------
    list
        Results of the query

    """
    r = requests.get(url, ujson.dumps(params))
    r.raise_for_status()
    return ujson.loads(r.text)


def _post(url, data):
    """RESTful API post (insert to database)

    Parameters
    ----------
    url: str
        Address for the amostra server
    data: dict
        Entries to be inserted to database

    """
    r = requests.post(url,
                      data=ujson.dumps(data))
    r.raise_for_status()
    return r.json()


def _put(url, query, update):
    """RESTful API put (update entries in database)

    Parameters
    ----------
    url: str
        Address for the amostra server
    query: dict
        Query string. Any pymongo supported mongo query
    update: dict
        Key/value pairs to be updated in the original document

    Returns
    -------
    bool
        True if update successful
    Raises
    --------
    requests.exceptions.HTTPError
        In case update fails, appropriate HTTPError and message string returned

    """
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
        """URL to the Amostra server"""
        return 'http://{}:{}/' .format(self.host, self.port)
    
    @property
    def _samp_url(self):
        """URL to the sample reference handler in the server side"""
        return self._server_path + 'sample'

    @property
    def _schema_url(self):
        """URL to the schema reference handler in the server side"""
        return self._server_path + 'schema'

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
        ins_doc : str
            The inserted document

        """
        doc = dict(uid=uid,
                   name=name, time=time,
                   container=doc_or_uid_to_uid(container) if container else 'NULL',
                   **kwargs)
        ins_doc = _post(self._samp_url, doc)
        return ins_doc[0]

    def create_sample_list(self, sample_list):
        """Insert a sample to the database

        Parameters
        ----------
        sample_list : list
            List of dictionaries

        Returns
        -------
        uid_list : list
            uid of the inserted documents

        """
        uid_list = []
        for s in sample_list:
            uid = _post(self._samp_url, s)
            uid_list.extend(uid)
        return uid_list

    def update(self, query, update):
        """Update a request given a query and name value pair to be updated. No upsert support.
        For more info on upsert, check Mongo documentations
        
        Parameters
        -----------
        query: dict
            Allows finding Sample documents to be updated
        update: dict
            Name/value pair that is to be replaced within an existing Request doc
        Returns
        ----------
        bool
            Returns True if update successful

        """
        _put(self._samp_url, query, update)
        return True

    def find(self, as_document=False, **kwargs):
        """
        Parameters
        ----------
        as_document: bool
            Formats output to doct.Document if True

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
        """Get information about schema from the server side

        Returns
        --------
        dict
            Returns the json schema dict used for validation

        """
        r = requests.get(self._schema_url,
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
        """URL to the Amostra server"""
        return 'http://{}:{}/' .format(self.host, self.port)

    @property
    def _req_url(self):
        """URL to the request reference handler in the server side"""
        return self._server_path + 'request'

    @property
    def _schema_url(self):
        """URL to the schema reference handler in the server side"""
        return self._server_path + 'schema'

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
        ins_doc: str
            The inserted Request document uid

        """

        payload = dict(uid=uid,
                       sample=doc_or_uid_to_uid(sample),
                       time=time, state=state,
                       seq_num=seq_num, **kwargs)
        ins_doc = _post(self._req_url, payload)
        return ins_doc[0]

    def find(self, as_document=False, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator

        Parameters
        -----------
        as_document: bool
            Format return type to doct.Document if set

        Yields
        ----------
        dict, doct.Document
            Result of the query

        Raises
        ---------
        StopIteration, requests.exceptions.HTTPError
            When nothing found or something is wrong on the server side. If server error occurs,
            a human friendly message is returned.

        """
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
        Returns
        ----------
        bool
            Returns True if update successful
        """
        _put(self._req_url, query, update)
        return True

    def get_schema(self):
        """Get information about schema from the server side

        Returns
        --------
        dict
            Returns the json schema dict used for validation
        """
        r = requests.get(self._schema_url,
                         params=ujson.dumps('request'))
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
        """URL to the Amostra server"""
        return 'http://{}:{}/' .format(self.host, self.port)

    @property
    def _cont_url(self):
        """URL to the container reference handler in the server side"""
        return self._server_path + 'container'

    @property
    def _schema_url(self):
        """URL to the schema reference handler in the server side"""
        return self._server_path + 'schema'

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
        ins_doc: str
            Inserted Container document uid
        """
        payload = dict(uid=uid,
                       time=time, **kwargs)
        ins_doc = _post(self._cont_url, payload)
        return ins_doc[0]

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
        Returns
        --------
        bool
            Returns True if update successful

        Returns
        ----------
        bool
            Returns True if update successful
        """
        _put(self._cont_url, query, update)
        return True

    def get_schema(self):
        """Get information about schema from the server side

        Returns
        --------
        dict
            Returns the json schema dict used for validation
        """
        r = requests.get(self._schema_url, params=ujson.dumps('container'))
        r.raise_for_status()
        return ujson.loads(r.text)