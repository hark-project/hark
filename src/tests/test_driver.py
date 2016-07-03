import unittest
import uuid

import hark.driver
import hark.driver.base
import hark.exceptions
import hark.models.machine
from hark.lib.command import which


class TestDriverWrapper(unittest.TestCase):

    def testListDrivers(self):
        d = hark.driver.drivers()
        assert isinstance(d, list)
        assert len(d) > 0

    def testGetDriver(self):
        m = hark.models.machine.Machine.new()
        d = hark.driver.get_driver('virtualbox', m)
        assert isinstance(d, hark.driver.base.BaseDriver)

        self.assertRaises(
            hark.exceptions.UnknownDriverException,
            hark.driver.get_driver, 'bla blah', m)

    def testIsAvailable(self):
        class Mock1(hark.driver.base.BaseDriver):
            cmd = which('true')

        assert Mock1.isAvailable() is True

        class Mock2(hark.driver.base.BaseDriver):
            cmd = str(uuid.uuid4())

        assert Mock2.isAvailable() is False
