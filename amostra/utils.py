import json
import os

import pkg_resources


def load_schema(filename):
    "Use pkg_resources the file in the installation; parse JSON; return dict."
    # Depending on how the package was installed, it might be located in
    # different places. This is the safe way to locate it that should always
    # work.
    relative_filepath = os.path.join('schemas', filename)
    abs_filepath = pkg_resources.resource_filename('amostra',
                                                   relative_filepath)
    with open(abs_filepath) as json_data:
        parsed = json.load(json_data)
    return parsed


def url_path_join(*pieces):
    """Join components of url into a relative url.

    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place.
    Copied from `notebook.utils.url_path_join`.
    """
    initial = pieces[0].startswith('/')
    final = pieces[-1].endswith('/')
    stripped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in stripped if s)

    if initial:
        result = '/' + result
    if final:
        result = result + '/'
    if result == '//':
        result = '/'

    return result
