import uuid

import jsonschema
from traitlets import (
    Dict,
    HasTraits,
    Instance,
    Integer,
    List,
    Unicode,
    default,
    validate,
)

from .utils import load_schema


def _validate_with_jsonschema(instance, proposal):
    """
    Validate that contents satisfy a jsonschema.

    This is meant to be used with traitlets' @validate decorator.
    """
    jsonschema.validate(instance.to_dict(), instance.SCHEMA)
    return proposal['value']


class AmostraDocument(HasTraits):
    """
    A HasTraits object with a reference to an amostra client.
    """
    uuid = Unicode(read_only=True)
    revision = Integer(0, read_only=True)

    def __init__(self, _amostra_client, *args, **kwargs):
        self._amostra_client = _amostra_client
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        # Configure _validate_with_jsonschema to validate all traits.
        trait_names = list(cls.class_traits())
        cls._validate = validate(*trait_names)(_validate_with_jsonschema)
        return super().__new__(cls, *args, **kwargs)

    @default('uuid')
    def _get_default_uuid(self):
        return str(uuid.uuid4())

    def __repr__(self):
        return (f'{self.__class__.__name__}(' +
                ', '.join(f'{name}={getattr(self, name)!r}'
                          for name, trait in self.traits().items()
                          if not trait.read_only) + ')')

    def to_dict(self):
        """
        Represent the object as a JSON-serializable dictionary.
        """
        return {name: getattr(self, name) for name in self.trait_names()}

    @classmethod
    def from_document(cls, amostra_client, document):
        """
        Convert a dict returned by the server to our traitlets-based object.
        """
        # Handle the read_only traits separately.
        uuid = document.pop('uuid')
        revision = document.pop('revision')
        instance = cls(amostra_client, **document)
        instance.set_trait('uuid', uuid)
        instance.set_trait('revision', revision)

        # Observe any updates to the instanceect and sync them to MongoDB.
        instance.observe(amostra_client._update)

        return instance

    def revisions(self):
        """
        Access all revisions of this document.

        Examples
        --------

        This returns a *generator* instance which lazily access the data, to
        enable partial or paginated access in case the number of revisions is
        large.

        To pull all revisions, use ``list``.

        >>> revisions = list(document.revisions())

        To pull the most recent revision use ``next``.

        >>> most_recent = next(document.revisions())
        """
        yield from self._amostra_client._revisions(self)

    def copy(self):
        # This gets, e.g. client.samples
        accessor = getattr(self._amostra_client,
                           TYPES_TO_COLLECTION_NAMES[type(self)])
        d = self.to_dict()
        d.pop('uuid')
        d.pop('revision')
        return accessor.new(**d)

    def purge(self):
        self._amostra_client._purge(type(self), self.uuid)

    def revert(self, num):
        # Find the one you want to revert to
        for it in self.revisions():
            if it.revision == num:
                break
        else:
            raise ValueError(f'revision {num} you were'
                             f'trying to revert to was not found')

        # Update current sample
        with self.hold_trait_notifications():
            for name, trait in self.traits().items():
                if not trait.read_only:
                    setattr(self, name, getattr(it, name))


class Institution(AmostraDocument):
    SCHEMA = load_schema('institution.json')
    name = Unicode()


class Owner(AmostraDocument):
    SCHEMA = load_schema('owner.json')
    name = Unicode()
    institutions = List(Instance(Institution))


class Project(AmostraDocument):
    SCHEMA = load_schema('project.json')
    name = Unicode()
    owners = List(Instance(Owner))


class Sample(AmostraDocument):
    SCHEMA = load_schema('sample.json')
    name = Unicode()
    projects = List(Unicode())
    composition = Unicode()
    tags = List(Unicode())
    description = Unicode()

    def __init__(self, _amostra_client, *, name, **kwargs):
        """
        This object should not be directly instantiated by this user. Use a client.

        Parameters
        ----------
        _amostra_client: Client
            The name is intended to avoid name collisions with any future
            sample traits.
        name: string
            A required Sample trait
        **kwargs
            Other, optional sample traits
        """
        super().__init__(_amostra_client, name=name, **kwargs)


class Container(AmostraDocument):
    SCHEMA = load_schema('container.json')
    name = Unicode()
    kind = Unicode()
    contents = Dict()

    def __init__(self, _amostra_client, *, name, kind, contents):
        """
        This object should not be directly instantiated by this user. Use a client.

        Parameters
        ----------
        _amostra_client: Client
            The name is intended to avoid name collisions with any future
            sample traits.
        **kwargs
            Other, optional sample traits
        """
        super().__init__(_amostra_client, name=name, kind=kind,
                         contents=contents)

    def to_dict(self):
        # Replace Sample objects in contents with their uuids.
        ret = super().to_dict()
        ret['contents'] = {k.uuid: v for k, v in ret['contents'].items()}
        return ret

    @classmethod
    def from_document(cls, amostra_client, document):
        """
        Convert a dict returned by the server to our traitlets-based object.
        """
        contents = {}
        # Replace {sample_uuid: location} with {Sample: location}.
        for sample_uuid, location in document['contents'].items():
            sample = amostra_client.samples.find_one({'uuid': sample_uuid})
            contents[sample] = location
        document['contents'] = contents
        return super().from_document(amostra_client, document)


TYPES_TO_COLLECTION_NAMES = {
    Container: 'containers',
    Sample: 'samples',
}
