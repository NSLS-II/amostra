""" Startup script for the server."""
import argparse
import tornado.web
from  amostra.server.backbone import (SampleReferenceHandler,
                                    RequestHandler,
                                    loop, db_connect)

from amostra.server.conf import load_configuration

def start_server():
    config = {k: v for k, v in load_configuration('amostra', 'AMST',
                                                  ['host', 'port', 'timezone',
                                                   'database'],
                                                  allow_missing=True).items() if v is not None}
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', dest='database', type=str,
                        help='name of database to use')
    parser.add_argument('--host', dest='host', type=str,
                        help='host to use')
    parser.add_argument('--timezone', dest='timezone', type=str,
                        help='Local timezone')
    parser.add_argument('--port', dest='port', type=int,
                        help='port to use to talk to mongo')
    parser.add_argument('--service-port', dest='service_port', type=int,
                        help='port listen to for clients')
    args = parser.parse_args()
    if args.database is not None:
        config['database'] = args.database
    if args.host is not None:
        config['host'] = args.host
    if args.timezone is not None:
        config['timezone'] = args.timezone
    if args.port is not None:
        config['port'] = args.port
    service_port = args.service_port
    if service_port is None:
        service_port = 7770

    db = db_connect(config['database'],
                    config['host'],
                    config['port'])
    print(db)
    application = tornado.web.Application([
        (r'/sample_ref', SampleReferenceHandler),
        (r'/request_ref', RequestHandler)
         ], db=db)
    application.listen(service_port)
    loop.start()