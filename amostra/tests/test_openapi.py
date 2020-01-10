import json
import os


def test_load():
    here = os.path.abspath(os.path.dirname(__file__))
    loc = os.path.join(here, '../../docs/source/openapi.json')
    with open(loc) as f:
        data = json.loads(f.read())
        assert data
