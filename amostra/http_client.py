import requests

from .objects import Container, Sample, Request, TYPES_TO_COLLECTION_NAMES
from .utils import url_path_join


class Client:
    """
    This connects to an amostra HTTP server for sample management.

    For each collection, we have a traitlets-based object to represent
    documents from that collection and automatically sync any changes back to
    the server to verify that they are valid and, if so, persist them in the
    database.
    """

    def __init__(self, url):
        """
        Connect to an amostra HTTP server.

        Parameters
        ----------
        url: string
        """
        self._session = requests.Session()
        self._url = url
        self._samples = CollectionAccessor(self, Sample)
        self._containers = CollectionAccessor(self, Container)
        self._requests = CollectionAccessor(self, Request)

    def _make_url(self, *pieces):
        return url_path_join(self._url, *pieces)

    @property
    def samples(self):
        """
        Accessor for creating and searching Samples
        """
        return self._samples

    @property
    def containers(self):
        """
        Accessor for creating and searching Containers
        """
        return self._containers

    @property
    def requests(self):
        """
        Accessor for creating and searching Requests
        """
        return self._requests

    def _new_document(self, obj_type, args, kwargs):
        """
        Insert a new document with a new uuid.
        """
        # Make a new object (e.g. Sample)
        obj = obj_type(self, *args, **kwargs)

        # Find the assocaited MongoDB collection.
        collection_name = TYPES_TO_COLLECTION_NAMES[obj_type]

        # Insert the new object.
        response = self._session.post(
            self._make_url(collection_name, 'new'),
            json={'parameters': obj.to_dict()})
        response.raise_for_status()

        # Let the server set the uuid.
        uuid = response.json()['uuid']
        obj.set_trait('uuid', uuid)
        obj.set_trait('revision', 0)  # paranoia

        # Observe any updates to the object and sync them to MongoDB.
        obj.observe(self._update)

        return obj

    def _update(self, change):
        """
        Sync a change to an object, observed via traitlets, to MongoDB.
        """
        # The 'revision' trait is a read-only trait, so if it is being changed
        # it is being changed by us, and we don't need to process it.
        # Short-circuit here to avoid an infinite recursion.
        if change['name'] == 'revision':
            return
        change = change.copy()
        owner = change.pop('owner')  # pop because it is not serializable
        collection_name = TYPES_TO_COLLECTION_NAMES[type(owner)]
        response = self._session.put(
            self._make_url(collection_name, owner.uuid),
            json={'change': change})
        response.raise_for_status()

    def _document_to_obj(self, obj_type, document):
        """
        Convert a dict returned by the server to our traitlets-based object.
        """
        # Handle the read_only traits separately.
        uuid = document.pop('uuid')
        revision = document.pop('revision')
        obj = obj_type(self, **document)
        obj.set_trait('uuid', uuid)
        obj.set_trait('revision', revision)

        # Observe any updates to the object and sync them to MongoDB.
        obj.observe(self._update)

        return obj

    def _revisions(self, obj):
        """
        Access all revisions to an object with the most recent first.
        """
        type_ = type(obj)
        collection_name = TYPES_TO_COLLECTION_NAMES[type_]
        response = self._session.get(
            self._make_url(collection_name, obj.uuid, 'revisions'))
        response.raise_for_status()
        for document in response.json()['revisions']:
            yield self._document_to_obj(type_, document)


class CollectionAccessor:
    """
    Accessor used on Clients
    """
    def __init__(self, client, obj_type):
        self._client = client
        self._obj_type = obj_type
        self._collection_name = TYPES_TO_COLLECTION_NAMES[self._obj_type]

    def new(self, *args, **kwargs):
        return self._client._new_document(self._obj_type, args, kwargs)

    def find(self, filter=None):
        if filter is None:
            filter = {}
        response = self._client._session.post(
            self._client._make_url(self._collection_name),
            json={'filter': filter})
        response.raise_for_status()
        for document in response.json()['results']:
            yield self._client._document_to_obj(self._obj_type, document)

    def find_one(self, filter):
        # TODO Improve the performance once pagination support is added.
        return next(self.find(filter))
