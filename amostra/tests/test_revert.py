import random
import string

from hypothesis import given, settings
from hypothesis import strategies as st


@given(names=st.lists(st.text(alphabet=string.ascii_lowercase,
                              min_size=1, max_size=4),
                      min_size=3, max_size=4, unique=True))
@settings(max_examples=10, deadline=1000)
def test_revert(client, names):
    n = len(names)
    s = client.samples.new(name=names[0])
    uuid = s.uuid
    for name in names[1:]:
        s.name = name

    num = random.randint(0, n-2)

    revert_target_cursor = client._db.samples_revisions.find({'revision': num,
                                                              'uuid': uuid})
    s.revert(num)
    target = next(revert_target_cursor)
    for name, trait in s.traits().items():
        if name == 'revision':
            continue
        else:
            assert getattr(s, name) == target[name]
