import uuid

import jsonschema
from traitlets import (
    default,
    HasTraits,
    Instance,
    Integer,
    Unicode,
    validate,
    )

from .utils import load_schema


class AmostraDocument(HasTraits):
    """
    A HasTraits object with a reference to an amostra client.
    """
    uuid = Unicode(read_only=True)
    revision = Integer(0, read_only=True)

    def __init__(self, _amostra_client, *args, **kwargs):
        self._amostra_client = _amostra_client
        super().__init__(*args, **kwargs)

    @default('uuid')
    def get_uuid(self):
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


def _validate_with_jsonschema(instance, proposal):
    """
    Validate that contents satisfy a jsonschema.

    This is meant to be used with traitlets' @validate decorator.
    """
    jsonschema.validate(instance.to_dict(), instance.SCHEMA)
    return proposal['value']


class Sample(AmostraDocument):
    SCHEMA = load_schema('sample.json')
    name = Unicode()

    _validate = validate('name')(_validate_with_jsonschema)

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

    validate('name')(_validate_with_jsonschema)

    def __init__(self, _amostra_client, **kwargs):
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
        super().__init__(_amostra_client, **kwargs)


class Request(AmostraDocument):
    SCHEMA = load_schema('request.json')
    sample = Instance(Sample)

    validate('sample')(_validate_with_jsonschema)

    def __init__(self, _amostra_client, *, sample, **kwargs):
        """
        This object should not be directly instantiated by this user. Use a client.

        Parameters
        ----------
        _amostra_client: Client
            The name is intended to avoid name collisions with any future
            sample traits.
        sample : Sample
        **kwargs
            Other, optional sample traits
        """
        super().__init__(_amostra_client, sample=sample, **kwargs)

    def to_dict(self):
        # Replace Sample object with Sample.uuid.
        ret = super().to_dict()
        ret['sample'] = ret['sample'].uuid
        return ret


TYPES_TO_COLLECTION_NAMES = {
    Container: 'containers',
    Sample: 'samples',
    Request: 'requests',
    }
