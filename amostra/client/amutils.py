import six


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
    if not isinstance(doc_or_uid, six.string_types):
        doc_or_uid = doc_or_uid['uid']
    return str(doc_or_uid)