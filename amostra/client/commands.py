from doct import Document
import ujson
import requests
from ..client import conf
from .amutils import doc_or_uid_to_uid, _get, _post, _put


class AmostraException(Exception):
    pass


class AmostraClient:
    def __init__(self, host, port):
        """ Simplified client for Sample, Request, and Container

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
    def _sample_client(self):
        """ Connection pool for Sample related tasks."""
        return SampleReference(host=self.host,
                               port=self.port)

    @property
    def _container_client(self):
        """Connection pool for Container related tasks."""
        return ContainerReference(host=self.host,
                                  port=self.port)

    @property
    def _request_client(self):
        """Connection pool for Request related tasks."""
        return RequestReference(host=self.host,
                                port=self.port)

    def create_sample(self, name, time=None, uid=None, container=None,
                       **kwargs):
        """ Insert a sample to the database

        Parameters
        ----------
        name : str
           The name of the sample  This must be unique in the database
        time: float
           The time sample is created. Client provided timestamp
        uid: str
            Unique identifier for a sample document
        container: str, list
            A single or a list of container documents or uids

        Returns
        -------
        str: The inserted document.

        """
        return self._sample_client.create(name=name, time=time, uid=uid,
                                          container=container, **kwargs)

    def create_request(self, sample=None, time=None,
                       uid=None, state='active', seq_num=0, **kwargs):
        """ Create a request entry in the dataase

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
        str: The inserted Request document uid

        """
        return self._request_client.create(sample=sample, time=time, uid=uid,
                                           state=state, seq_num=seq_num,
                                           **kwargs)

    def create_container(self, uid=None, time=None, **kwargs):
        """ Insert a container document.

        Parameters
        ----------
        uid: str
        Unique identifier for a Container document
        time: float
        Time document created. Client side timestamp

        Returns
        -------
        str: Inserted Container document uid

        """
        return self._container_client.create(uid=uid, time=time, **kwargs)

    def update_sample(self, update, query):
        """Update a sample given a query and name value pair to be updated.
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
        return self._sample_client.update(update=update, query=query)

    def update_request(self, update, query):
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
        if self._request_client.update(update=update, query=query):
            return True
        return False

    def update_container(self, update, query):
        """Update a container given a query and name value pair to be updated.
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
        if self._container_client.update(update=update, query=query):
            return True
        return False

    def find_sample(self, as_document=True, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator

        Parameters
        -----------
        as_document: bool
            Format return type to doct.Document if set

        Yields
        ----------
       list
            Result of the query, list of samples doct.Document


        """
        return list(self._sample_client.find(as_document=as_document,
                                                 **kwargs))

    def find_request(self, as_document=True, **kwargs):
        """Given a set of mongo search parameters, return a list of requests

        Parameters
        -----------
        as_document: bool
            Format return type to doct.Document if set

        Returns
        ----------
        list
            Result of the query, list of doct.Document

        """
        return list(self._request_client.find(as_document=as_document,
                                              **kwargs))

    def find_container(self, as_document=True, **kwargs):
        """Given a set of mongo search parameters, return a requests iterator

        Parameters
        -----------
        as_document: bool
            Format return type to doct.Document if set

        Yields
        ----------
       list
            Result of the query, list of containers doct.Document

        """
        return list(self._container_client.find(as_document=as_document,
                                                **kwargs))

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
            The inserted document uid

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
        """ Create a request entry in the dataase
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
