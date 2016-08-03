import unittest
try:
    from unittest.mock import call, patch
except ImportError:
    from mock import call, patch

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
