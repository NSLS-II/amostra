from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import tornado.ioloop
import tornado.web
from tornado import gen

import pymongo
import pymongo.errors as perr
import ujson as json
from amostra.server import utils
from jsonschema.exceptions import ValidationError, SchemaError



class AmostraException(Exception): # gotta find a less general one for this
    pass


def db_connect(database, host, port):
    """Helper function to deal with stateful connections to MongoDB
    Connection established lazily. Connects to do database, not
    
    
    Parameters
    ----------
    database: str
        The name of database pymongo creates and/or connects
    host: str
        Name/address of the server that mongo daemon lives
    port: int
        Port num of the server
    Returns pymongo.database.Database
    -------
        Async server object which comes in handy as server has to juggle multiple clients
        and makes no difference for a single client compared to pymongo
    """
    try:
        client = pymongo.MongoClient(host=host, port=port)
    except perr.ConnectionFailure:
        raise AmostraException("Unable to connect to MongoDB server. Make sure Mongo is up and running")
    database = client[database]
    return database

def _compose_err_msg(code, status, m_str=''):
    fmsg = status + str(m_str)
    return tornado.web.HTTPError(code, fmsg)

class DefaultHandler(tornado.web.RequestHandler):
    """DefaultHandler which takes care of CORS. Javascript needs this"""
    @tornado.web.asynchronous
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def data_received(self, chunk):
        """Abstract method, here to show it exists explicitly. Useful for streaming client"""
        pass


class SampleReferenceHandler(DefaultHandler):
    """Handler for SampleReference insert, update, and querying.
    A RESTful handler, nothing fancy or stateful about this
    
    Methods
    --------
    get()
        Query 'sample_referenece' documents given certain parameters.
    Pass 'num' in order to obtain the last 'num' sample references. 

    post()
        Insert 'sample_reference' documents 

    put()
        Update 'sample_reference' documents provided new version or updated field
    """
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        database = settings['db']
        query = utils.unpack_params(self)
        num = query.pop("num", None)
        if num:
            try:
                docs = database.sample_reference.find().sort('time', 
                                                         direction=pymongo.DESCENDING).limit(num)
            except pymongo.errors.PyMongoError:
                raise _compose_err_msg(500, 'Query failed: ', query)
        else:
            try:
                docs = database.sample_reference.find(query).sort('time',
                                                                  direction=pymongo.DESCENDING).limit(num)
            except pymongo.error.PyMongoError:
                raise _compose_err_msg(500, 'Query Failed: ', query)
        if docs:
            utils.return2client(self, docs)
        else:
            raise _compose_err_msg(500, 'No results found!')

    @tornado.web.asynchronous
    def post(self):
        database = self.settings['db']
        data = ujson.loads(self.request.body.decode("utf-8"))
        try:
            json.validate(data, utils.schemas['sample_reference'])
        except (ValidationError, SchemaError):
            raise _compose_err_msg(400, "Invalid schema on document(s)", data)
        try:
            res = database.sample_reference.insert(data)
        except pymongo.errors.PyMongoError:
            raise _compose_err_msg(500, 'Validated data can not be inserted', data)
        # database.sample_reference.create_index([()])

    @tornado.web.asynchronous
    def put(self):
        #TODO: Check update documentation. Seems like I donot remember the docs well
        database = settings['db']
        query = utils.unpack_params(self)
        database.sample_reference.update(query, {'$set':update}, upsert=False)


class RequestReferenceHandler(DefaultHandler):
    @tornado.web.asynchronous
    def get(self):
        pass

    @tornado.web.asynchronous
    def post(self):
        pass

    @tornado.web.asynchronous
    def put(self):
        # TODO: Implement upsert
        pass
