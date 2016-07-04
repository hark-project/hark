import unittest

from hark.exceptions import (
    ModelInvalidException,
    InvalidMachineException
)
from hark.models import (
    BaseModel,
    SQLModel,
)
from hark.models.machine import Machine
from hark.models.port_mapping import PortMapping


class TestBaseModel(unittest.TestCase):
    def test_base_model_json(self):
        "Test that subclassing still only uses dict elements for JSON"
        class mymodel(BaseModel):
            foo = '1'

        m = mymodel()
        m['a'] = 'b'
        assert m.json() == '{"a": "b"}'

    def test_missing_required(self):
        "Test that an exception is thrown when missing required"
        class mymodel(BaseModel):
            fields = ['a', 'b']
            required = ['a', 'b']

        ins = mymodel(a=1)
        self.assertRaises(ModelInvalidException, ins.validate)
        ins = mymodel(a=1, b=2)
        assert ins.validate() is None


class TestSQLModel(unittest.TestCase):
    def test_validate(self):
        class mymodel(SQLModel):
            table = 'a'
            key = 'b'
            fields = ['c', 'd']

        mymodel().validate()

    def test_missing_fields(self):
        "Test that an exception is thrown when missing fields definition"
        class mymodel(BaseModel):
            table = 'a'
            key = 'b'

        ins = mymodel(c=1)
        self.assertRaises(ModelInvalidException, ins.validate)

    def test_missing_required(self):
        "Test that an exception is thrown when missing required"
        class mymodel(BaseModel):
            table = 'a'
            key = 'b'
            fields = ['c', 'd']
            required = ['c', 'd']

        ins = mymodel(c=1)
        self.assertRaises(ModelInvalidException, ins.validate)

    def test_missing_key(self):
        class mymodel(SQLModel):
            table = 'a'
            fields = ['hi']
        ins = mymodel()
        self.assertRaises(ModelInvalidException, ins.validate)

    def test_missing_table(self):
        class mymodel(SQLModel):
            key = 'a'
            fields = ['hi']
        ins = mymodel()
        self.assertRaises(ModelInvalidException, ins.validate)


class TestMachine(unittest.TestCase):
    def test_new(self):
        m = Machine.new(name='foo', driver='bar', guest='bang', memory_mb=512)
        assert m.validate() is None

    def test_new_with_id(self):
        args = dict(machine_id='a')
        self.assertRaises(InvalidMachineException, Machine.new, **args)

    def test_minimum_memory(self):
        m = Machine.new(name='foo', driver='bar', guest='bang', memory_mb=100)
        self.assertRaises(InvalidMachineException, m.validate)

    def test_machine_id_length(self):
        m = Machine.new(name='foo', driver='bar', guest='bang')
        assert len(m['machine_id']) == 8
        m2 = Machine.new(name='foo', driver='bar', guest='bang')
        assert m2['machine_id'] == m['machine_id']


class TestPortMapping(unittest.TestCase):
    def test_port_mapping_virtualbox(self):
        pm = PortMapping(
            host_port=11, guest_port=22, machine_id='blah', name='bleh')
        pm.validate()
        expect = 'bleh,tcp,127.0.0.1,11,,22'
        assert pm.format_virtualbox() == expect
