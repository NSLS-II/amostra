import argparse
import tornado.web
import sys
import tornado.ioloop
import tornado.options
from  amostra.server.engine import (SampleReferenceHandler,
                                    RequestReferenceHandler,
                                    SchemaHandler,
                                    ContainerReferenceHandler,
                                    db_connect)
from .server.conf import load_configuration


def start_server(config=None):
    """
    Amostra service startup script.
    Returns tornado event loop provided configuration.

    Parameters
    ----------
    config: dict
        Command line arguments always have priority over local config or
        yaml files.Using these parameters,  a tornado event loop is created.
        Keep in mind that this server is started in lazy fashion.
        It does not verify
        the existence of a mongo instance running on the specified location.
    """
    if not config:
        config = {k: v for k, v in load_configuration('amostra', 'AMST',
                                                      ['mongo_uri',
                                                       'timezone',
                                                       'database',
                                                       'service_port'],
                                                      allow_missing=True).items() if v is not None}
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', dest='database', type=str,
                        help='name of database to use')
    parser.add_argument('--mongo_uri',
                         dest='mongo_uri', type=str,
                        help='URI for connecting to central MongoDB')
    parser.add_argument('--timezone', dest='timezone', type=str,
                        help='Local timezone')
    parser.add_argument('--service-port', dest='service_port', type=int,
                        help='port listen to for clients')
    args = parser.parse_args()
    if args.database is not None:
        config['database'] = args.database
    if args.mongo_uri is not None:
        config['mongo_uri'] = args.mongo_uri
    elif not config["mongo_uri"]:
        raise KeyError('mongo_uri must be defined')
    if args.timezone is not None:
        config['timezone'] = args.timezone
    service_port = args.service_port
    if service_port is None:
        service_port = 7770
    print(args)
    db = db_connect(database=config['database'],
                    mongo_uri=config['mongo_uri'])
    application = tornado.web.Application([
        (r'/sample', SampleReferenceHandler),
        (r'/request', RequestReferenceHandler),
        (r'/container', ContainerReferenceHandler),
        (r'/schema', SchemaHandler)
         ], db=db)
    print('Starting Amostra service with configuration ', config)
    application.listen(service_port)
    tornado.ioloop.IOLoop.current().start()
