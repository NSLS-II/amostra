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
