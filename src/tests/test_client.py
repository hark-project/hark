import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import hark.client
import hark.dal
import hark.exceptions

from hark.models.machine import Machine


class TestLocalClient(unittest.TestCase):
    """
    Basic tests of LocalClient with a mocked-out DAL.
    """

    @patch('hark.context.Context._initialize')
    @patch('hark.dal.DAL._connect')
    @patch('hark.context.ImageCache._initialize')
    def setUp(self, mockInit, mockConnect, mockCacheInit):
        self.ctx = hark.context.Context('balooga')
        assert mockInit.called
        assert mockConnect.called
        assert mockCacheInit.called

    def testMachines(self):
        m = Machine(
                machine_id='1', name='foo',
                driver='yes', guest='no', memory_mb=512)

        mockRead = MagicMock(return_value=[m])
        self.ctx.dal.read = mockRead

        client = hark.client.LocalClient(self.ctx)

        machines = client.machines()

        assert isinstance(machines, list)
        assert len(machines) == 1
        assert machines[0] == m
        mockRead.assert_called_with(Machine)

    def testSaveMachine(self):
        m = Machine.new(name='foo', driver='yes', guest='no', memory_mb=512)

        mockSave = MagicMock(return_value=None)
        self.ctx.dal.create = mockSave

        client = hark.client.LocalClient(self.ctx)

        client.createMachine(m)

        mockSave.assert_called_with(m)

    def testGetMachine(self):
        m = Machine.new(name='foo', driver='yes', guest='no', memory_mb=512)
        client = hark.client.LocalClient(self.ctx)

        mockRead = MagicMock(return_value=[])
        self.ctx.dal.read = mockRead
        self.assertRaises(
            hark.exceptions.MachineNotFound,
            client.getMachine, m['name'])

        mockRead = MagicMock(return_value=[m])
        self.ctx.dal.read = mockRead
        assert client.getMachine(m['name']) == m

    def testLog(self):
        tf = tempfile.mktemp()
        try:
            msg = "ajlssljskl"
            with open(tf, 'w') as f:
                f.write(msg)

            self.ctx.log_file = MagicMock(return_value=tf)
            client = hark.client.LocalClient(self.ctx)

            logs = client.log()
            assert logs == msg
        finally:
            os.remove(tf)
