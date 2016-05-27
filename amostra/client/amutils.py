import requests
import ujson


def doc_or_uid_to_uid(doc_or_uid):
    """Given Document or uid return the uid

    Parameters
    ----------
    doc_or_uid : dict or str
        If str, then assume uid and pass through, if not, return
        the 'uid' field

    Returns
    -------
    uid : str
        A string version of the uid of the given document
    """
    try:
        return str(doc_or_uid['uid'])
    except TypeError:
        return doc_or_uid


def _get(url, params):
    """RESTful API get (querying)

    Parameters
    ----------
    url: str
        Address for the amostra server
    params: dict
        Query parameters to be sent to mongo instance

    Returns
    -------
    list
        Results of the query

    """
    r = requests.get(url, ujson.dumps(params))
    r.raise_for_status()
    return ujson.loads(r.text)


def _post(url, data):
    """RESTful API post (insert to database)

    Parameters
    ----------
    url: str
        Address for the amostra server
    data: dict
        Entries to be inserted to database

    """
    r = requests.post(url,
                      data=ujson.dumps(data))
    r.raise_for_status()
    return r.json()


def _put(url, query, update):
    """RESTful API put (update entries in database)

    Parameters
    ----------
    url: str
        Address for the amostra server
    query: dict
        Query string. Any pymongo supported mongo query
    update: dict
        Key/value pairs to be updated in the original document

    Returns
    -------
    bool
        True if update successful
    Raises
    --------
    requests.exceptions.HTTPError
        In case update fails, appropriate HTTPError and message string returned

    """
    update_cont = {'query': query, 'update': update}
    r = requests.put(url,
                     data=ujson.dumps(update_cont))
    r.raise_for_status()
