from amostra.utils import load_schema
from hypothesis import given, strategies as st
from hypothesis import settings
import hypothesis_jsonschema

d = load_schema('sample.json')
d['required'] = ['name']
d['properties'].pop('uuid')
d['properties'].pop('revision')
d['properties']['name']['minLength'] = 3
d['properties']['name']['maxLength'] = 5
d['additionalProperties'] = False
st_sample = hypothesis_jsonschema.from_schema(d)

@given(st.lists(st_sample, unique_by = lambda x: x['name'], min_size = 3, max_size=5))
@settings(max_examples=1)
def test_new(samples_list):
    for sample in samples_list:
        print(sample)
