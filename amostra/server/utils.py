import tornado.web
from pkg_resources import resource_filename as rs_fn
import ujson
import pymongo
import uuid
import time as ttime

class AmostraException(Exception):
    pass


SCHEMA_PATH = 'schemas'
SCHEMA_NAMES = {'sample': 'sample.json',
                'request': 'request.json',
                'container': 'container.json'}
fn = '{}/{{}}'.format(SCHEMA_PATH)
schemas = {}
for name, filename in SCHEMA_NAMES.items():
    try:
        with open(rs_fn('amostra',
                        resource_name=fn.format(filename))) as fin:
            schemas[name] = ujson.load(fin)
    except FileNotFoundError:
        raise AmostraException('Schema file not found or does not exist')


def compose_err_msg(code, status, m_str=''):
    fmsg = str(status) + str(m_str)
    return tornado.web.HTTPError(status_code=code, reason=fmsg)


def unpack_params(handler):
    """Unpacks the queries from the body of the header
    Parameters
    ----------
    handler: tornado.web.RequestHandler
        Handler for incoming request to collection
    Returns dict
    -------
        Unpacked query in dict format.
    """
    if isinstance(handler, tornado.web.RequestHandler):
        return ujson.loads(list(handler.request.arguments.keys())[0])
    else:
        raise TypeError("Wrong type")


def return2client(handler, payload):
    """Home brew solution to dump the result back to client's open socket.
    No need to worry about package size or socket behavior as
    tornado handles this for us
    Parameters
    -----------
    handler: tornado.web.RequestHandler
        Request handler for the collection of operation(post/get)
    payload: dict, list
        Information to be sent to the client
    """
    # TODO: Solve precision issue with json precision
    if isinstance(payload, pymongo.cursor.Cursor):
            l = []
            for p in payload:
                del(p['_id'])
                l.append(p)
            handler.write(ujson.dumps(l))
    elif isinstance(payload, dict):
        del(payload['_id'])
        handler.write(ujson.dumps(list(payload)))
    else:
        handler.write('[')
        d = next(payload)
        while True:
            try:
                del(d['_id'])
                handler.write(ujson.dumps(d))
                d = next(payload)
                handler.write(',')
            except StopIteration:
                break
        handler.write(']')
    handler.finish()


def default_timeuid(document):
    """
    Given a document, default time and uid fields if not provided

    Parameters
    ----------
    document: dict
        Document to be inserted

    Returns
    -------
    dict
        Document with defaults
    """
    if 'uid' not in document or document['uid'] is None:
        document['uid'] = str(uuid.uuid4())
    if 'time' not in document or document['time'] is None:
        document['time'] = ttime.time()
    return document
