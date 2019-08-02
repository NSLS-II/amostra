import uuid

import jsonschema
from traitlets import (
    default,
    HasTraits,
    Integer,
    Unicode,
    validate,
    )

from .utils import load_schema


class VersionedDocument(HasTraits):
    """
    A HasTraits object with a uuuid, revision number, and convenience methods.
    """
    uuid = Unicode(read_only=True)
    revision = Integer(0, read_only=True)

    @default('uuid')
    def get_uuid(self):
        return str(uuid.uuid4())

    def __repr__(self):
        return (f'{self.__class__.__name__}(' +
                ', '.join(f'{name}={getattr(self, name)!r}'
                          for name, trait in self.traits().items()
                          if not trait.read_only) + ')')

    def to_dict(self):
        return {name: getattr(self, name) for name in self.trait_names()}


def _validate_with_jsonschema(instance, proposal):
    """
    Validate that contents satisfy a jsonschema.

    This is meant to be used with traitlets' @validate decorator.
    """
    jsonschema.validate(instance.to_dict(), instance.SCHEMA)
    return proposal['value']


class Sample(VersionedDocument):
    SCHEMA = load_schema('sample.json')
    name = Unicode()
#     sample_desc": sample_desc,
#     "date_created": date_created,
#     "user_id": user_id,
#     "project_name": project_name,
#     "institution_id": institution_id,
#     "composition": composition,
#     "density": density,
#     "thickness": thickness,
#     "notes": notes,
#     "state": state,
#     "current_bar_id": current_bar_id,
#     "current_slot_name": current_slot_name,
#     "past_bar_ids": past_bar_ids,
#     "location_id": location_id,
#     "requests": requests,
#     "history": history,
#     "priority": priority
# }

    validate('name')(_validate_with_jsonschema)

    def __init__(self, *, name, **kwargs):
        super().__init__(name=name, **kwargs)


class Request(VersionedDocument):
    SCHEMA = load_schema('request.json')
    name = Unicode()
#     sample_desc": sample_desc,
#     "date_created": date_created,
#     "user_id": user_id,
#     "project_name": project_name,
#     "institution_id": institution_id,
#     "composition": composition,
#     "density": density,
#     "thickness": thickness,
#     "notes": notes,
#     "state": state,
#     "current_bar_id": current_bar_id,
#     "current_slot_name": current_slot_name,
#     "past_bar_ids": past_bar_ids,
#     "location_id": location_id,
#     "requests": requests,
#     "history": history,
#     "priority": priority
# }

    validate('name')(_validate_with_jsonschema)

    def __init__(self, *, name, **kwargs):
        super().__init__(name=name, **kwargs)
