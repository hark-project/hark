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
        expectBindings = [1, 2]
        assert re.match(expect, qr) is not None
        assert 'answer' in qr
        assert 'boot' in qr

        assert len(expectBindings) == 2
        assert 1 in expectBindings
        assert 2 in expectBindings


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
