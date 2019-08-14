import amostra.mongo_client
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from hypothesis import settings
from pymongo import MongoClient
import random
import uuid


alphabet_list = ''
for i in range(26):
    alphabet_list = alphabet_list + chr(97 + i)


@given(names = st.lists(st.text(alphabet=alphabet_list, min_size=1, max_size=4), min_size=3, max_size=4, unique=True))
@settings(max_examples = 10, deadline = 1000)
def test_revert(url, names):
    db_name = str(uuid.uuid4())
    client = amostra.mongo_client.Client(url + db_name)

    n = len(names)
    s = client.samples.new(name = names[0])
    for name in names[1:]:
        s.name = name

    num = random.randint(0, n-2)

    revert_target_cursor = client._db.samples_revisions.find({'revision': num})
    s.revert(num)
    target = next(revert_target_cursor)
    for name, trait in s.traits().items():
        if name is 'revision':
            continue
        else:
            assert getattr(s, name) == target[name]

    MongoClient(url).drop_database(db_name)
