import pytest
from .testing import _baseSM
from amostra.basic import SampleReference
from io import StringIO
import json
import yaml


class TestBasic(_baseSM):
    db_class = SampleReference
    args = ()
    kwargs = {}

    def test_disk_round_trip(self):
        db = self.db_class(*self.args, **self.kwargs)
        tt = StringIO()

        def _helper(doc_list):
            db2 = SampleReference(doc_list)
            for doc in db.find():
                doc_id = doc['uid']
                rl_doc = db2.find(uid=doc_id)
                assert doc == rl_doc

        for exp, imp in ((db.dump_to_json, json.loads),
                         (db.dump_to_yaml, yaml.load)):
            tt = StringIO()
            exp(tt)
            rt = imp(tt.getvalue())
            yield _helper, rt

    def test_constructor_fails(self):
        def _helper(rt, excp):
            with pytest.raises(excp):
                SampleReference(rt)

        rt_lst = [[{'uid': '123', 'name': 'foo'},
                   {'uid': '123', 'name': 'bar'}],
                  [{'uid': '123', 'name': 'foo'},
                   {'uid': '456', 'name': 'foo'}]]
        for rt in rt_lst:
            yield _helper, rt, ValueError
        yield _helper, [{'uid': '123'}], KeyError
        yield _helper, [{'name': 'foo'}], KeyError
