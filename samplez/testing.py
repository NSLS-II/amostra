import pytest


class _baseSM:

    @classmethod
    def setup_class(cls):
        db = cls.db = cls.db_class(*cls.args, **cls.kwargs)
        for n in ['squeekalina', 'squawky', 'squakawaka']:
            db.add(n, species='penguin', location='aquarium', family='bird')
        for n in ['puffin', 'puffy', 'puffinini']:
            db.add(n, species='puffin', location='zoo', family='bird')
        db.add(name='Fredrick', location='zoo', species='aardvark')

    def test_add(self):
        db = self.db
        uid = db.add(name='Lionel', location='zoo', species='aardvark')
        find_res = list(db.find(name='Lionel'))
        assert len(find_res) == 1
        assert find_res[0]['uid'] == uid

    def test_update(self):
        db = self.db
        uid = db.add(name='samantha', location='home', occupation='zoo goer')
        original = list(db.find(uid=uid))[0]
        old, new = db.update(uid, location='zoo')
        assert old == original
        assert new['location'] == 'zoo'

        with pytest.raises(ValueError):
            db.update(uid, name='casper')

    def test_find(self):
        def _helper(kwargs, n):
            ret = list(self.db.find(**kwargs))
            assert len(ret) == n

        t_vals = [({'family': 'bird'}, 6),
                  ({'species': 'penguin'}, 3),
                  ({'species': 'puffin'}, 3),
                  ({'location': 'zoo', 'family': 'bird'}, 3)]

        for kw, n in t_vals:
            yield _helper, kw, n

    def test_add_fail(self):
        db = self.db
        with pytest.raises(ValueError):
            db.add(name='Fredrick', color='gray')

    def test_update_overwrite(self):
        db = self.db
        uid = db.add(name='linkt', location='VR')
        with pytest.raises(ValueError):
            db.update(uid, overwrite=False, location='R')
