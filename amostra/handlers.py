from jsonschema.exceptions import ValidationError
from tornado import web
from tornado.escape import json_decode


class CreateHandler(web.RequestHandler):
    def post(self, collection_name):
        parameters = json_decode(self.request.body)['parameters']
        accessor = getattr(self.settings['mongo_client'], collection_name)
        parameters.pop('uuid')
        parameters.pop('revision')
        try:
            obj = accessor.new(**parameters)
        except ValidationError:
            self.write_error(403)
        self.write({'uuid': obj.uuid})


class SearchHandler(web.RequestHandler):
    def post(self, collection_name):
        filter = json_decode(self.request.body)['filter']
        accessor = getattr(self.settings['mongo_client'], collection_name)
        # TODO Add pagination.
        results = list(accessor.find(filter))
        self.write({"results": [result.to_dict() for result in results]})


class ObjectHandler(web.RequestHandler):
    def get(self, collection_name, uuid):
        accessor = getattr(self.settings['mongo_client'], collection_name)
        result = accessor.find_one({'uuid': uuid})
        self.write(result.to_dict())

    def put(self, collection_name, uuid):
        change = json_decode(self.request.body)['change']
        accessor = getattr(self.settings['mongo_client'], collection_name)
        change['owner'] = accessor.find_one({'uuid': uuid})
        client = self.settings['mongo_client']
        try:
            client._update(change)
        except ValidationError:
            self.write_error(403)
        self.finish()


class RevisionsHandler(web.RequestHandler):
    def get(self, collection_name, uuid):
        accessor = getattr(self.settings['mongo_client'], collection_name)
        result = accessor.find_one({'uuid': uuid})
        # TODO Add pagination.
        revisions = result.revisions()
        self.write({"revisions": [revision.to_dict() for revision in revisions]})


def init_handlers():
    # POST /samples/new
    # POST /samples
    # GET /samples/<uuid>
    # PUT /samples/<uuid>
    return [(r'/([A-Za-z0-9_\.\-]+)/new/?', CreateHandler),
            (r'/([A-Za-z0-9_\.\-]+)/([A-Za-z0-9_\.\-]+)/?', ObjectHandler),
            (r'/([A-Za-z0-9_\.\-]+)/([A-Za-z0-9_\.\-]+)/revisions/?',
             RevisionsHandler),
            (r'/([A-Za-z0-9_\.\-]+)/?', SearchHandler),
            ]
