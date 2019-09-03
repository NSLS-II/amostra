import hypothesis_jsonschema
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from amostra.utils import load_schema

sample_dict = load_schema("sample.json")
# Pop uuid and revision cause they are created automatically
sample_dict['properties'].pop('uuid')
sample_dict['properties'].pop('revision')
# sample_dict['properties']['name']['minLength'] = 1
sample_dict['required'] = sample_dict['required'][2:]
st_sample = hypothesis_jsonschema.from_schema(sample_dict)

container_dict = load_schema("container.json")
container_dict['properties'].pop('uuid')
container_dict['properties'].pop('revision')
# container_dict['properties']['name']['minLength'] = 1
container_dict['required'] = container_dict['required'][2:]
st_container = hypothesis_jsonschema.from_schema(container_dict)


@given(samples_list=st.lists(st_sample, unique_by=lambda x: x['name'], min_size=3, max_size=5),
       containers_list=st.lists(st_container, unique_by=lambda x: x['name'], min_size=3, max_size=5))
@settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
def test_new(client, samples_list, containers_list):
    contents_dict = dict()
    for sample in samples_list:
        client.samples.new(**sample)
        s = client.samples.new(**sample)
        contents_dict[s] = 'LOCATION'

    for container in containers_list:
        container['contents'] = contents_dict
        client.containers.new(**container)
