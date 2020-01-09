import json
def test_load():
    with open('../../docs/source/openapi.json') as f:
        data = json.loads(f.read())
        assert data
