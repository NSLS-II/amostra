from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import tornado.web
from tornado import gen
import pymongo
import jsonschema
import ujson
from amostra.server import utils
from jsonschema.exceptions import ValidationError, SchemaError
from pymongo.errors import PyMongoError


def db_connect(database, mongo_host, mongo_port):
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
        client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
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
        num = query.pop("num", None)
        if num:
            try:
                docs = database.sample.find().sort('time',
                                        direction=pymongo.DESCENDING).limit(num)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, 'Query on sample has failed', query)
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
                uids.append(d['uid'])
                res = database.sample.insert(d)
                database.sample.create_index([('uid', pymongo.DESCENDING)], unique=True, 
                                             background=True)
                database.sample.create_index([('time', pymongo.DESCENDING),
                                              ('name', pymongo.DESCENDING)], unique=False,
                                             background=True)
                database.sample.create_index([('container', pymongo.DESCENDING)],
                                               unique=False, sparse=True)
        elif isinstance(data, dict):
            try:
                jsonschema.validate(data,
                                    utils.schemas['sample'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            uids.append(data['uid'])
            
            res = database.sample.insert(data)
            # if inserted, create indices that are certainly being indexed            
            if res:
                database.sample.create_index([('uid', pymongo.DESCENDING)],
                                             unique=True, background=True)
                database.sample.create_index([('time', pymongo.DESCENDING)],
                                             unique=False, background=True)
        else:
            raise utils._compose_err_msg(500,
                                         status='SampleHandler expects list or dict')        
        self.finish(ujson.dumps(uids))

    @tornado.web.asynchronous
    def put(self):
        # TODO: Make sure no unique field gets updated!
        database = self.settings['db']
        incoming = ujson.loads(self.request.body)
        try:
            query = incoming.pop('query')
            update = incoming.pop('update')
        except KeyError:
            raise utils._compose_err_msg(500, 
                                         status='filter and update are both required fields')
        if any(x in update.keys() for x in ['uid', 'time']):
            raise utils._compose_err_msg(500,
                                   status='Time and uid cannot be updated')
        print('update query', query)
        print('update field', update)
        res = database.sample.update_many(filter=query,
                                           update={'$set': update},
                                           upsert=False)
        self.finish(ujson.dumps(res.raw_result))


class RequestReferenceHandler(DefaultHandler):
    @tornado.web.asynchronous
    def get(self):
        database = self.settings['db']
        query = utils.unpack_params(self)
        num = query.pop("num", None)
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
                docs = database.request.find(query).sort('time',
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
                                        utils.schemas['request'])
                except (ValidationError, SchemaError):
                    raise utils._compose_err_msg(400,
                                                 "Invalid schema on document(s)", d)
                try:
                    res = database.request.insert(d)
                    uids.append(d['uid'])
                except pymongo.errors.PyMongoError:
                    raise utils._compose_err_msg(500,
                                                 'Validated data can not be inserted',
                                                 data)
                database.request.create_index([('uid', pymongo.DESCENDING)],
                                             unique=True, background=True)
                database.request.create_index([('time', pymongo.DESCENDING)],
                                             unique=False, background=True)
                database.request.create_index([('sample', pymongo.DESCENDING)],
                                             unique=False, background=True, sparse=True)
        elif isinstance(data, dict):
            try:
                jsonschema.validate(data,
                                    utils.schemas['request'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            try:
                res = database.request.insert(data)
                uids.append(data['uid'])
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500,
                                             'Validated data can not be inserted',
                                             data)
            database.request.create_index([('uid', pymongo.DESCENDING)],
                                             unique=True, background=True)
            database.request.create_index([('time', pymongo.DESCENDING)],
                                             unique=False, background=True)
            database.request.create_index([('sample', pymongo.DESCENDING)],
                                             unique=False, background=True, sparse=True)
        else:
            raise utils._compose_err_msg(500,
                                         status='SampleHandler expects list or dict')
        self.finish(ujson.dumps(uids))
    
    @tornado.web.asynchronous
    def put(self):
        # TODO: Make sure no unique field gets updated!
        database = self.settings['db']
        incoming = ujson.loads(self.request.body)
        try:
            query = incoming.pop('query')
            update = incoming.pop('update')
        except KeyError:
            raise utils._compose_err_msg(500, 
                                         status='filter and update are both required fields')
        if any(x in update.keys() for x in ['uid', 'time', 'name']):
            raise utils._compose_err_msg(500,
                                         status='Time and uid cannot be updated')
        res = database.request.update_many(filter=query,
                                           update={'$set': update},
                                           upsert=False)
        self.finish(ujson.dumps(res.raw_result))
        

class ContainerReferenceHandler(DefaultHandler):
    """Handler for SampleReference insert, update, and querying.
    A RESTful handler, nothing fancy or stateful about this

    Methods
    --------
    get()
        Query 'container' documents given certain parameters.
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
        num = query.pop("num", None)
        if num:
            try:
                docs = database.sample.find().sort('time', direction=pymongo.DESCENDING).limit(num)
            except pymongo.errors.PyMongoError:
                raise utils._compose_err_msg(500, '', query)
        else:
            try:
                docs = database.container.find(query).sort('time',
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
                                        utils.schemas['container'])
                except (ValidationError, SchemaError):
                    raise utils._compose_err_msg(400,
                                                 "Invalid schema on document(s)", d)
                uids.append(d['uid'])
                res = database.container.insert(d)
                database.container.create_index([('uid', pymongo.DESCENDING)],
                                                unique=True, background=True)
                database.container.create_index([('time', pymongo.DESCENDING)],
                                                unique=False, background=True)
                database.container.create_index([('container', pymongo.DESCENDING)],
                                                unique=False, background=True, sparse=True)
        elif isinstance(data, dict):
            try:
                jsonschema.validate(data,
                                    utils.schemas['container'])
            except (ValidationError, SchemaError):
                raise utils._compose_err_msg(400,
                                             "Invalid schema on document(s)", data)
            uids.append(data['uid'])
            res = database.container.insert(data)
            if res:
                database.request.create_index([('uid', pymongo.DESCENDING)],
                                                 unique=True, background=True)
                database.request.create_index([('time', pymongo.DESCENDING)],
                                            unique=False, background=True)
        else:
            raise utils._compose_err_msg(500,
                                         status='SampleHandler expects list or dict')        
        self.finish(ujson.dumps(uids))

    @tornado.web.asynchronous
    def put(self):
        # TODO: Make sure no unique field gets updated!
        database = self.settings['db']
        incoming = ujson.loads(self.request.body)
        try:
            query = incoming.pop('query')
            update = incoming.pop('update')
        except KeyError:
            raise utils._compose_err_msg(500, 
                                         status='filter and update are both required fields')
        if any(x in update.keys() for x in ['uid', 'time', 'name']):
            raise utils._compose_err_msg(500,
                                   status='Time and uid cannot be updated')
        res = database.container.update_many(filter=query,
                                           update={'$set': update},
                                           upsert=False)
        self.finish(ujson.dumps(res.raw_result))


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