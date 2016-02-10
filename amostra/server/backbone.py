from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import tornado.ioloop
import tornado.web
from tornado import gen

import pymongo
import pymongo.errors as perr

import ujson
import jsonschema


class AmostraException(Exception): # gotta find a less general one for this
    pass


def db_connect(database, host, port):
    """Helper function to deal with stateful connections to motor.
    Connection established lazily.
    Parameters
    ----------
    database: str
        The name of database pymongo creates and/or connects
    host: str
        Name/address of the server that mongo daemon lives
    port: int
        Port num of the server
    Returns pymongo.MotorDatabase
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
    @tornado.web.asynchronous
    def get(self):
        #   Yields all documents which have all of the keys equal
        # to the kwargs.  ex ::
        pass

    @tornado.web.asynchronous
    def post(self):
        # TODO: Obtain a schema and validate against it!
        # TODO: If a schema is provided, index required fields
        # if no schema, simply insert into db
        pass

    @tornado.web.asynchronous
    def put(self):
        # TODO: Implement upsert
        # Since no transactions
        # make a copy of the data being updated
        # in case smth goes wrong, return it to client alongside
        # attempted update and an error code
        pass


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
