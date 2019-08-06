import pymongo

from .objects import TYPES_TO_COLLECTION_NAMES, Container, Sample


class Client:
    """
    This connects to several MongoDB collections for sample management.

    For each collection, we have a traitlets-based object to represent
    documents from that collection and automatically sync any changes back to
    the database.

    Each collection has a counterpart named {collection_name}_revisions that
    stores previous version of the document. This approach was inspired by:
    https://www.mongodb.com/blog/post/building-with-patterns-the-document-versioning-pattern
    """

    def __init__(self, database):
        """
        Connect to a MongoDB datbase.

        Parameters
        ----------
        database: pymongo.Database or URI string
        """
        if database is None:
            raise ValueError("Database should be URI or pymongo-like object.")
        if isinstance(database, str):
            database = _get_database(database)
        self._db = database
        self._samples = CollectionAccessor(self, Sample)
        self._containers = CollectionAccessor(self, Container)

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

    def _new_document(self, obj_type, args, kwargs):
        """
        Insert a new document with a new uuid.
        """
        # Make a new object (e.g. Sample)
        obj = obj_type(self, *args, **kwargs)

        # Find the assocaited MongoDB collection.
        collection_name = TYPES_TO_COLLECTION_NAMES[obj_type]
        collection = self._db[collection_name]

        # Insert the new object.
        collection.insert(obj.to_dict())

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
        owner = change['owner']
        collection_name = TYPES_TO_COLLECTION_NAMES[type(owner)]
        collection = self._db[collection_name]
        revisions = self._db[f'{collection_name}_revisions']
        filter = {'uuid': owner.uuid}
        update = {'$set': {change['name']: change['new']},
                  '$inc': {'revision': 1}}
        # TODO Use transactions for this once we have MongoDB 4.0+.
        # Increment the revision number.
        owner.set_trait('revision', owner.revision + 1)
        # Update the document in {collection_name}.
        original = collection.find_one_and_update(filter, update)
        # Remove the internal MongoDB id.
        original.pop('_id')
        # Insert the old version in {collection_name}_revisions
        revisions = revisions.insert(original)

    def _document_to_obj(self, obj_type, document):
        """
        Convert a dict returned by pymongo to our traitlets-based object.
        """
        # Remove the internal MongoDB id.
        document.pop('_id')

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
        revisions = self._db[f'{TYPES_TO_COLLECTION_NAMES[type(obj)]}_revisions']
        type_ = type(obj)
        for document in (revisions.find({'uuid': obj.uuid})
                                  .sort('revision', pymongo.DESCENDING)):
            yield self._document_to_obj(type_, document)


class CollectionAccessor:
    """
    Accessor used on Clients
    """
    def __init__(self, client, obj_type):
        self._client = client
        self._obj_type = obj_type
        self._collection = client._db[TYPES_TO_COLLECTION_NAMES[self._obj_type]]

    def new(self, *args, **kwargs):
        return self._client._new_document(self._obj_type, args, kwargs)

    def find(self, filter):
        if filter is None:
            filter = {}
        for document in self._collection.find(filter):
            yield self._client._document_to_obj(self._obj_type, document)

    def find_one(self, filter):
        return self._client._document_to_obj(
            self._obj_type, self._collection.find_one(filter))


def _get_database(uri):
    client = pymongo.MongoClient(uri)
    try:
        # Called with no args, get_database() returns the database
        # specified in the client's uri --- or raises if there was none.
        # There is no public method for checking this in advance, so we
        # just catch the error.
        return client.get_database()
    except pymongo.errors.ConfigurationError as err:
        raise ValueError(
            f"Invalid client: {client} "
            f"Did you forget to include a database?") from err
