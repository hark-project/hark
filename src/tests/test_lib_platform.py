from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import hark.exceptions
import hark.lib.platform


class TestSupports(TestCase):

    @patch('multiprocessing.cpu_count')
    def test_cpu_cores(self, mockCpuCount):
        mockCpuCount.return_value = 2
        assert hark.lib.platform.cpu_cores() == 2

    @patch('hark.lib.platform.platform')
    def test_supports(self, mockPlatform):
        mockPlatform.return_value = 'linux'

        assert hark.lib.platform.supports('qemu')
        assert hark.lib.platform.supports('virtualbox')

        mockPlatform.return_value = 'linux2'

        assert hark.lib.platform.supports('qemu')
        assert hark.lib.platform.supports('virtualbox')

        mockPlatform.return_value = 'darwin'
        assert not hark.lib.platform.supports('qemu')
        assert hark.lib.platform.supports('virtualbox')

        mockPlatform.return_value = 'freebsd7'
        assert not hark.lib.platform.supports('qemu')
        assert hark.lib.platform.supports('virtualbox')

        mockPlatform.return_value = 'freebsd10'
        assert not hark.lib.platform.supports('qemu')
        assert hark.lib.platform.supports('virtualbox')

        mockPlatform.return_value = 'blerr'
        self.assertRaises(
            hark.exceptions.UnknownPlatformException,
            hark.lib.platform.supports, 'virtualbox')
