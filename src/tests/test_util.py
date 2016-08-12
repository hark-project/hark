import unittest
from unittest.mock import call, patch

import hark.util


class TestGetFreePort(unittest.TestCase):
    def test_getFreePort(self):

        p = hark.util.getFreePort()

        assert isinstance(p, int)

    @patch('socket.socket.getsockname')
    def test_getFreePort_exclude(self, mockGetSockName):
        mockGetSockName.side_effect = [
            ('', 1000), ('', 1001), ('', 1002), ('', 1003),
        ]
        p = hark.util.getFreePort(exclude=[1000, 1001, 1002])

        # port should be 1003 and it should have been called four times
        assert p == 1003
        mockGetSockName.asset_has_calls([call(), call(), call(), call()])


class TestCheckHarkEnv(unittest.TestCase):

    @patch('getpass.getuser')
    def test_CheckHarkEnv(self, mockGetUser):
        # check that a normal user is fine
        mockGetUser.return_value = 'blah'
        hark.util.checkHarkEnv()

        # check that root is not fine
        mockGetUser.return_value = 'root'
        self.assertRaises(
            hark.exceptions.BadHarkEnvironment, hark.util.checkHarkEnv)
