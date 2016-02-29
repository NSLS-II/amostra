""" Startup script for the server."""
import argparse
import tornado.web
import tornado.ioloop
from  amostra.server.engine import (SampleReferenceHandler, 
                                    RequestReferenceHandler,
                                    SchemaHandler, db_connect)
from amostra.server.conf import load_configuration


def start_server(config=None):
    print('Here i am')
    if not config:
        config = {k: v for k, v in load_configuration('amostra', 'AMST',
                                                      ['mongo_host', 'mongo_port', 'timezone',
                                                       'database', 'service_port'],
                                                      allow_missing=True).items() if v is not None}
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', dest='database', type=str,
                        help='name of database to use')
    parser.add_argument('--mongo_host',
                         dest='mongo_host', type=str,
                        help='host to use')
    parser.add_argument('--timezone', dest='timezone', type=str,
                        help='Local timezone')
    parser.add_argument('--mongo_port', dest='mongo_port', type=int,
                        help='port to use to talk to mongo')
    parser.add_argument('--service-port', dest='service_port', type=int,
                        help='port listen to for clients')
    args = parser.parse_args()
    if args.database is not None:
        config['database'] = args.database
    if args.mongo_host is not None:
        config['mongo_host'] = args.host
    if args.timezone is not None:
        config['timezone'] = args.timezone
    if args.mongo_port is not None:
        config['mongo_port'] = args.port
    service_port = args.service_port
    if service_port is None:
        service_port = 7770
    print(config)
    db = db_connect(config['database'],
                    config['mongo_host'],
                    config['mongo_port'])
    print(db)
    application = tornado.web.Application([
        (r'/sample', SampleReferenceHandler),
        (r'/request', RequestReferenceHandler),
        (r'/schema', SchemaHandler)
         ], db=db)
    application.listen(service_port)
    tornado.ioloop.IOLoop.current().start()