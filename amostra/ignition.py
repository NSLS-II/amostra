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
                                                      ['mongo_host',
                                                       'mongo_port', 'timezone',
                                                       'database',
                                                       'service_port'],
                                                      allow_missing=True).items() if v is not None}
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', dest='database', type=str,
                        help='name of database to use')
    parser.add_argument('--mongo-host',
                         dest='mongo_host', type=str,
                        help='host to use')
    parser.add_argument('--timezone', dest='timezone', type=str,
                        help='Local timezone')
    parser.add_argument('--mongo-port', dest='mongo_port', type=int,
                        help='port to use to talk to mongo')
    parser.add_argument('--service-port', dest='service_port', type=int,
                        help='port listen to for clients')
    parser.add_argument('--no-auth', dest='auth', action='store_false')
    parser.add_argument('--auth', dest='auth', action='store_true')
    parser.set_defaults(auth=False)
    parser.add_argument('--mongo-user', dest='mongo_user', type=str,
                            help='Mongo username')
    parser.add_argument('--mongo-pwd', dest='mongo_pwd', type=str,
                            help='Mongo password')
    args = parser.parse_args()
    print(args)
    if args.database is not None:
        config['database'] = args.database
    if args.mongo_host is not None:
        config['mongo_host'] = args.mongo_host
    if args.timezone is not None:
        config['timezone'] = args.timezone
    if args.mongo_port is not None:
        config['mongo_port'] = args.mongo_port
    service_port = args.service_port
    if service_port is None:
        service_port = 7770
    if args.auth:
        if args.mongo_user and args.mongo_pwd:
            config['mongo_user'] = args.mongo_user
            config['mongo_pwd'] = args.mongo_pwd
        else:
            raise KeyError('--mongo-user and --mongo-pwd required with auth')
    else:
        config['mongo_user'] = None
        config['mongo_pwd'] = None
    db = db_connect(database=config['database'],
                    mongo_host=config['mongo_host'],
                    mongo_port=config['mongo_port'],
                    mongo_user=config['mongo_user'],
                    mongo_pwd=config['mongo_pwd'],
                    auth=args.auth)
    application = tornado.web.Application([
        (r'/sample', SampleReferenceHandler),
        (r'/request', RequestReferenceHandler),
        (r'/container', ContainerReferenceHandler),
        (r'/schema', SchemaHandler)
         ], db=db)
    print('Starting Amostra service with configuration ', config)
    application.listen(service_port)
    tornado.ioloop.IOLoop.current().start()
