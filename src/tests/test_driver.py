import unittest
from unittest.mock import call, patch
import uuid

import hark.driver
import hark.driver.base
import hark.driver.status
import hark.exceptions
import hark.models.machine
from hark.lib.command import which


class TestStatus(unittest.TestCase):
    def test_status_str(self):
        assert str(hark.driver.status.RUNNING) == 'running'


class TestDriverWrapper(unittest.TestCase):

    def testListDrivers(self):
        d = hark.driver.drivers()
        assert isinstance(d, list)
        assert len(d) > 0

    def testGetDriver(self):
        m = hark.models.machine.Machine.new(guest='Debian-8')
        d = hark.driver.get_driver('virtualbox', m)
        assert isinstance(d, hark.driver.base.BaseDriver)

        self.assertRaises(
            hark.exceptions.UnknownDriverException,
            hark.driver.get_driver, 'bla blah', m)

    @patch('hark.lib.platform.platform')
    def testGetDriverUnsupported(self, mockPlatform):
        mockPlatform.return_value = 'darwin'
        m = hark.models.machine.Machine.new()
        self.assertRaises(
            hark.exceptions.UnsupportedDriverException,
            hark.driver.get_driver, 'qemu', m)

    def testIsAvailable(self):
        class Mock1(hark.driver.base.BaseDriver):
            cmd = which('true')

        assert Mock1.isAvailable() is True

        class Mock2(hark.driver.base.BaseDriver):
            cmd = str(uuid.uuid4())

        assert Mock2.isAvailable() is False


class TestDriverBase(unittest.TestCase):

    @patch('hark.driver.virtualbox.Driver.status')
    def testAssertStatus(self, mockStatus):
        mockStatus.return_value = hark.driver.status.STOPPED

        d = hark.driver.virtualbox.Driver({'guest': 'Debian-8'})

        valid = (hark.driver.status.STOPPED,)
        mockStatus.return_value = hark.driver.status.STOPPED
        d.assertStatus('blah', *valid)

        valid = (hark.driver.status.STOPPED, hark.driver.status.RUNNING)
        mockStatus.return_value = hark.driver.status.STOPPED
        d.assertStatus('blah', *valid)

        valid = (hark.driver.status.RUNNING,)
        mockStatus.return_value = hark.driver.status.STOPPED
        self.assertRaises(
            hark.exceptions.InvalidStatus,
            d.assertStatus, 'blah', *valid)

    @patch('hark.driver.virtualbox.Driver.status')
    def testWaitStatus(self, mockStatus):
        from hark.driver.status import RUNNING, STOPPED
        mockStatus.side_effect = [
            STOPPED, STOPPED, RUNNING
        ]
        d = hark.driver.virtualbox.Driver({'name': 'hi', 'guest': 'Debian-8'})
        d.waitStatus(RUNNING, interval_ms=1)

        mockStatus.assert_has_calls([call(), call(), call()])
