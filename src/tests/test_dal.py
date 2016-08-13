import collections
import os
import re
import tempfile
import unittest

from hark.dal import (
    DAL,
    InMemoryDAL
)
from hark.exceptions import InvalidQueryConstraint, DuplicateModelException
from hark.models import SQLModel
from hark.models.machine import Machine


class MockDAL(DAL):
    def __init__(self):
        pass


class TestDAL(unittest.TestCase):
    def test_init(self):
        f = tempfile.mktemp()
        assert not os.path.exists(f)
        DAL(f)
        assert os.path.exists(f)

        # test that we can instantiate again
        DAL(f)

        # cleanup
        os.remove(f)

    def test_init_memory(self):
        d = InMemoryDAL()
        assert not os.path.exists(d.path)


class TestDALQueries(unittest.TestCase):
    def setUp(self):
        self.db = MockDAL()

    def test_read_query(self):

        class mymodel(SQLModel):
            table = 'oof'
            key = 'heya'
            fields = ['a', 'b']

        qr = self.db._read_query(mymodel)
        expect = "SELECT a, b FROM oof;"
        assert qr == expect

        qr = self.db._read_query(mymodel, constraints=dict(a=5))
        expect = "SELECT a, b FROM oof WHERE a = 5;"
        assert qr == expect

        qr = self.db._read_query(mymodel, constraints=dict(b="bleh"))
        expect = "SELECT a, b FROM oof WHERE b = 'bleh';"
        assert qr == expect

        cons = collections.OrderedDict()
        cons["a"] = 5
        cons["b"] = "bleh"
        qr = self.db._read_query(mymodel, constraints=cons)
        expect = "SELECT a, b FROM oof WHERE a = 5 AND b = 'bleh';"
        assert qr == expect

        cons = {"a": {}}
        self.assertRaises(
            InvalidQueryConstraint,
            self.db._read_query, mymodel, constraints=cons)

    def test_insert_query(self):

        class mymodel(SQLModel):
            table = 'bleh'
            key = 'blop'
            fields = ['answer', 'boot']

        fields = collections.OrderedDict()
        fields['answer'] = 1
        fields['boot'] = 2
        ins = mymodel(**fields)
        ins.validate()

        qr, bindings = self.db._insert_query(ins)

        expect = r"INSERT INTO bleh \(\w+, \w+\) VALUES \(\?, \?\);"
        assert re.match(expect, qr) is not None
        assert 'answer' in qr
        assert 'boot' in qr

        assert len(bindings) == 2
        assert 1 in bindings
        assert 2 in bindings

    def test_insert_query_null(self):
        class mymodel(SQLModel):
            table = 'bleh'
            key = 'answer'
            fields = ['answer', 'boot']

        fields = collections.OrderedDict()
        fields['answer'] = 1
        fields['boot'] = None
        ins = mymodel(**fields)
        ins.validate()

        qr, bindings = self.db._insert_query(ins)

        assert len(bindings) == 2
        assert 1 in bindings
        assert None in bindings

    def test_key_constraints(self):
        class mymodel(SQLModel):
            table = 'bleh'
            key = 'answer'
            fields = ['answer', 'boot']

        ins = mymodel(answer=1, boot=2)
        ins.validate()
        cons = self.db._key_constraints(ins)
        assert cons == {'answer': 1}

        class mymodel2(SQLModel):
            table = 'bleh'
            key = ['answer', 'boot']
            fields = ['answer', 'boot']

        ins = mymodel2(answer=1, boot=2)
        ins.validate()
        cons = self.db._key_constraints(ins)
        assert cons == {'answer': 1, 'boot': 2}

    def test_delete_query(self):
        class mymodel(SQLModel):
            table = 'bleh'
            key = 'answer'
            fields = ['answer', 'boot']

        instance = mymodel(answer='hi', boot='fsjdlk')
        qr = self.db._delete_query(instance)
        expect = "DELETE FROM bleh WHERE answer = 'hi';"
        assert qr == expect

        class mymodel2(SQLModel):
            table = 'bleh'
            key = ['answer', 'boot']
            fields = ['answer', 'boot']

        ins = mymodel2(answer='hi', boot='blo')
        qr = self.db._delete_query(ins)
        expect = "DELETE FROM bleh WHERE answer = 'hi' AND boot = 'blo';"
        expect2 = "DELETE FROM bleh WHERE boot = 'blo' AND answer = 'hi';"
        assert qr == expect or qr == expect2


class TestDALCRUD(unittest.TestCase):
    "Tests real operations against the DAL"

    def setUp(self):
        self.dal = InMemoryDAL()

    def test_create_read(self):
        ins = Machine.new(
            name='foo', driver='blah',
            guest='bleh', memory_mb=512)
        self.dal.create(ins)

        res = self.dal.read(Machine)
        assert len(res) == 1
        assert len(ins.keys()) == len(res[0].keys())
        for k, v in ins.items():
            assert res[0][k] == v

        ins = Machine.new(
            name='blah', driver='blah',
            guest='blorgh', memory_mb=512)
        self.dal.create(ins)
        res = self.dal.read(Machine)
        assert len(res) == 2

        res = self.dal.read(Machine, constraints={"name": "foo"})
        assert len(res) == 1

    def test_create_read_nulls(self):
        ins = Machine.new(
            name='foo', driver=None,
            guest='bleh', memory_mb=512)
        self.dal.create(ins)

        constraints = {'driver': None}
        res = self.dal.read(Machine, constraints=constraints)
        assert len(res) == 1
        assert len(ins.keys()) == len(res[0].keys())
        for k, v in ins.items():
            assert res[0][k] == v

    def test_create_dup(self):
        ins = Machine.new(
            name='foo', driver='blah',
            guest='bleh', memory_mb=512)
        self.dal.create(ins)

        ins = Machine.new(
            name='foo', driver='blah',
            guest='bleh', memory_mb=512)
        self.assertRaises(
            DuplicateModelException,
            self.dal.create, ins)

    def test_create_delete_read(self):
        """
        Test that we can create then delete an object and then not read it.
        """
        ins = Machine.new(
            name='foo', driver='blah',
            guest='bleh', memory_mb=512)
        self.dal.create(ins)
        res = self.dal.read(Machine)
        assert len(res) == 1

        # delete it and make sure we have no rows
        self.dal.delete(ins)

        res = self.dal.read(Machine)
        assert len(res) == 0

        # now make sure we can create 1 things and only delete 1
        ins = Machine.new(
            name='foo', driver='blah',
            guest='bleh', memory_mb=512)
        ins2 = Machine.new(
            name='bar', driver='blah',
            guest='bleh', memory_mb=512)
        self.dal.create(ins)
        self.dal.create(ins2)

        res = self.dal.read(Machine)
        assert len(res) == 2

        self.dal.delete(ins)
        res = self.dal.read(Machine)
        assert len(res) == 1
        assert res[0]['machine_id'] == ins2['machine_id']
