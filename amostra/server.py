import logging
import os

import tornado.options
from tornado import httpserver, ioloop, log, web
from tornado.options import define, options

from .handlers import init_handlers
from .mongo_client import Client


def init_options():
    default_host, default_port = '0.0.0.0', 5000
    define("base_url", help='Base URL of app')
    define("mongo_uri", help='URI of MongoDB')
    define("debug", default=False, help="run in debug mode", type=bool)
    define("sslcert", help="path to ssl .crt file", type=str)
    define("sslkey", help="path to ssl .key file", type=str)
    define("host", default=default_host, help="run on the given interface", type=str)
    define("port", default=default_port, help="run on the given port", type=int)


def make_app():
    # DEBUG env implies both autoreload and log-level
    if os.environ.get("DEBUG"):
        options.debug = True
        logging.getLogger().setLevel('DEBUG')

    settings = dict(
        base_url=options.base_url,
        mongo_client=Client(options.mongo_uri)
    )
    handlers = init_handlers()
    return web.Application(handlers, debug=options.debug, **settings)


def main(argv=None):
    init_options()
    tornado.options.parse_command_line(argv)

    try:
        from tornado.curl_httpclient import curl_log
    except ImportError as e:
        log.app_log.warning("Failed to import curl: %s", e)
    else:
        # debug-level curl_log logs all headers, info for upstream requests,
        # which is just too much.
        curl_log.setLevel(max(log.app_log.getEffectiveLevel(), logging.INFO))

    # create and start the app
    app = make_app()

    # load ssl options
    ssl_options = None
    if options.sslcert:
        ssl_options = {
            'certfile': options.sslcert,
            'keyfile': options.sslkey,
        }

    http_server = httpserver.HTTPServer(app, xheaders=True, ssl_options=ssl_options)
    log.app_log.info("Listening on %s:%i, path %s", options.host, options.port,
                     app.settings['base_url'])
    http_server.listen(options.port, options.host)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
