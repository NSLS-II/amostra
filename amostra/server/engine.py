from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import tornado.web
from tornado import gen
import pymongo
import jsonschema
import pymongo.errors
import ujson
from amostra.server import utils
from jsonschema.exceptions import ValidationError, SchemaError
from pymongo.errors import PyMongoError


def db_connect(database, host, port):
    """Helper function to deal with stateful connections to MongoDB
    Connection established lazily. Connects to the database on request.
    Same connection pool is used for all clients per recommended by
    tornado developer manual.

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
        Async server object which comes in handy as server has to juggle
    multiple clients and makes no difference for a single client compared
    to pymongo
    """
    try:
        client = pymongo.MongoClient(host=host, port=port)
    except pymongo.errors.ConnectionFailure:
        raise utils.AmostraException("Unable to connect to MongoDB server...")
    database = client[database]
    return database


class DefaultHandler(tornado.web.RequestHandler):
    """DefaultHandler which takes care of CORS. Javascript needs this.
    In general, methods on RequestHandler and elsewhere in Tornado
    are not thread-safe. In particular, methods such as write(),
    finish(), and flush() must only be called from the main thread.
    If you use multiple threads it is important to use IOLoop.add_callback
    to transfer control back to the main thread before finishing the request.
    """
    @tornado.web.asynchronous
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def data_received(self, chunk):
        """Abstract method, overwrite potential default"""
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
        Insert 'sample' documents

    put()
        Update or Insert if 'sample' document does not exist.
    Update supports both field update and document replacement. If you
    would like to replace a document, simply provide a full doc in update
    field. Otherwise, provide a dict that holds the new value and field name.
    Returns the total number of documents that are updated.
    """
    @tornado.web.asynchronous
    def get(self):
        database = self.settings['db']
        query = utils.unpack_params(self)
        print(query)
        num = query.pop("num", None)
        # TODO: Time should always be required!
        if num:
            try:
                docs = database.sample.find().sort('time',
                                                             direction=pymongo.DESCENDING).limit(num)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, '', query)
        else:
            try:
                docs = database.sample.find(query).sort('time',
                                                                  direction=pymongo.DESCENDING)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, 'Query Failed: ', query)
        if docs:
            utils.return2client(self, docs)
        else:
            raise utils._compose_err_msg(500, 'No results found!')

    @tornado.web.asynchronous
    def post(self):
        database = self.settings['db']
        data = ujson.loads(self.request.body.decode("utf-8"))
        uids = []
        if isinstance(data, list):
            for d in data:
                try:
                    jsonschema.validate(d,
                                        utils.schemas['sample'])
                except (ValidationError, SchemaError):
                    raise utils._compose_err_msg(400,
                                                 "Invalid schema on document(s)", d)
                try:
                    res = database.sample.insert(d)
                    uids.append(d['uid'])
                except pymongo.errors.PyMongoError:
                    raise utils._compose_err_msg(500,
                                                 'Validated data can not be inserted',
                                                 data)
                # database.sample.create_index([()])
        elif isinstance(data, dict):
            try:
                jsonschema.validate(data,
                                    utils.schemas['sample'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            try:
                res = database.sample.insert(data)
                uids.append(data['uid'])
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500,
                                             'Validated data can not be inserted',
                                             data)
            # database.sample.create_index([()])
        else:
            raise utils._compose_err_msg(500,
                                         status='SampleHandler expects list or dict')        
        self.finish(ujson.dumps(uids))

    @tornado.web.asynchronous
    def put(self):
        # TODO: Check update documentation.
        database = self.settings['db']
        incoming = utils.unpack_params(self)
        query = incoming['query']
        update = incoming['update']
        database.sample.update_many(query,
                                              {'$set': update},
                                              upsert=False)


class RequestReferenceHandler(DefaultHandler):
    @tornado.web.asynchronous
    def get(self):
        database = self.settings['db']
        query = utils.unpack_params(self)
        print(query)
        num = query.pop("num", None)
        # TODO: Time should always be required!
        if num:
            try:
                docs = database.reference.find().\
                                        sort('time',
                                             direction=pymongo.DESCENDING).\
                                                       limit(num)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, '', query)
        else:
            try:
                docs = database.reference.find(query).sort('time',
                                                           direction=pymongo.DESCENDING)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, 'Query Failed: ', query)
        if docs:
            utils.return2client(self, docs)
        else:
            raise utils._compose_err_msg(500, 'No results found!')

    @tornado.web.asynchronous
    def post(self):
        database = self.settings['db']
        data = ujson.loads(self.request.body.decode("utf-8"))
        uids = []
        print(data)
        if isinstance(data, list):
            for d in data:
                try:
                    jsonschema.validate(d,
                                        utils.schemas['reference'])
                except (ValidationError, SchemaError):
                    raise utils._compose_err_msg(400,
                                                 "Invalid schema on document(s)", d)
                try:
                    res = database.reference.insert(d)
                    uids.append(d['uid'])
                except pymongo.errors.PyMongoError:
                    raise utils._compose_err_msg(500,
                                                 'Validated data can not be inserted',
                                                 data)
                # database.sample.create_index([()])
        elif isinstance(data, dict):
            try:
                jsonschema.validate(data,
                                    utils.schemas['reference'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            try:
                res = database.reference.insert(data)
                uids.append(data['uid'])
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500,
                                             'Validated data can not be inserted',
                                             data)
            # database.sample.create_index([()])
        else:
            raise utils._compose_err_msg(500,
                                         status='SampleHandler expects list or dict')        
        self.finish(ujson.dumps(uids))

    @tornado.web.asynchronous
    def put(self):
        # TODO: Implement upsert
        pass


class SchemaHandler(DefaultHandler):
    """Provides the json used for schema validation provided collection name"""
    @tornado.web.asynchronous
    def get(self):
        col = utils.unpack_params(self)
        utils.return2client(self, utils.schemas[col])

    @tornado.web.asynchronous
    def put(self):
        raise utils._compose_err_msg(405, 
                                     status='Not allowed on server')

    @tornado.web.asynchronous
    def post(self):
        raise utils._compose_err_msg(405, 
                                     status='Not allowed on server')