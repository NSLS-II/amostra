from hypothesis import given, strategies as st
from hypothesis.strategies import text
from hypothesis import settings
import random


alphabet_list = ''
for i in range(26):
    alphabet_list = alphabet_list + chr(97 + i)


@given(names = st.lists(st.text(alphabet=alphabet_list, min_size=1, max_size=4), min_size=3, max_size=4, unique=True))
@settings(max_examples = 10, deadline = 1000)
def test_revert(client_conf, names):
    client, mongo_client = client_conf()
    n = len(names)
    s = client.samples.new(name = names[0])
    for name in names[1:]:
        s.name = name

    num = random.randint(0, n-2)

    revert_target_cursor = mongo_client['tests-amostra'].samples_revisions.find({'revision': num})
    s.revert(num)
    target = next(revert_target_cursor)
    for name, trait in s.traits().items():
        if name is 'revision':
            continue
        else:
            assert getattr(s, name) == target[name]
