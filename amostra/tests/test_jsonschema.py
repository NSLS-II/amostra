import hypothesis_jsonschema
from hypothesis import given, settings
from hypothesis import strategies as st

from amostra.utils import load_schema

sample_dict = load_schema("sample.json")
# Pop uuid and revision cause they are created automatically
sample_dict['properties'].pop('uuid')
sample_dict['properties'].pop('revision')
sample_dict['required'] = ['name']
sample_dict['properties']['name']['minLength'] = 3
sample_dict['properties']['name']['maxLength'] = 5
sample_dict['additionalProperties'] = False
st_sample = hypothesis_jsonschema.from_schema(sample_dict)


container_dict = load_schema("container.json")
container_dict['properties'].pop('uuid')
container_dict['properties'].pop('revision')
container_dict['required'] = ['name', 'kind', 'contents']
container_dict['properties']['name']['minLength'] = 3
container_dict['properties']['name']['maxLength'] = 5
sample_dict['additionalProperties'] = False
st_container = hypothesis_jsonschema.from_schema(container_dict)


@given(samples_list=st.lists(st_sample, unique_by=lambda x: x['name'], min_size=3, max_size=5),
       containers_list=st.lists(st_container, unique_by=lambda x: x['name'], min_size=3, max_size=5))
@settings(max_examples=3)
def test_new(client, samples_list, containers_list):
    contents_dict = dict()
    for sample in samples_list:
        assert client.samples.new(**sample)
        s = client.samples.new(**sample)
        contents_dict[s] = 'LOCATION'

    for container in containers_list:
        container['contents'] = contents_dict
        print(client.containers.new(**container))
