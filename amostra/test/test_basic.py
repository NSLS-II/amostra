from amostra.testing import _baseSM, TESTING_CONFIG
from amostra.client.commands import SampleReference


class TestBasicSampleRef(_baseSM):
    db_class = SampleReference
    args = ()
    kwargs = {}
    db_class.host = TESTING_CONFIG['host']
    db_class.port = TESTING_CONFIG['port']

    def test_disk_round_trip(self):
        db = self.db_class(*self.args, **self.kwargs)

        def _helper(doc_list):
            db2 = SampleReference(doc_list)
            for doc in db.find():
                doc_id = doc['uid']
                rl_doc = db2.find(uid=doc_id)
                assert doc == rl_doc
