from tornado import web
from tornado.escape import json_decode


class CreateHandler(web.RequestHandler):
    def post(self, obj_type):
        content = json_decode(self.request.body)
        client = self.settings['mongo_client']
        obj = client.new_sample(**content)
        self.write({'uuid': obj.uuid})


class SearchHandler(web.RequestHandler):
    def post(self, obj_type):
        filter = json_decode(self.request.body)['filter']
        client = self.settings['mongo_client']
        # TODO Add pagination.
        results = list(client.find_samples(filter))
        self.write({"results": [result.to_dict() for result in results]})


class ObjectHandler(web.RequestHandler):
    def get(self, obj_type):
        filter = json_decode(self.request.body)['filter']
        client = self.settings['mongo_client']
        # TODO Add pagination.
        results = list(client.find_samples(filter))
        self.write(results)
        self.finish()


def init_handlers():
    return [(r'/([A-Za-z0-9_\.\-]+)/new/?', CreateHandler),
            (r'/([A-Za-z0-9_\.\-]+)//?', SearchHandler),
            (r'/([A-Za-z0-9_\.\-]+)/(.+)/?', ObjectHandler),
            ]
