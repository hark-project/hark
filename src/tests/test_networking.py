from unittest import TestCase

import hark.exceptions
import hark.networking


class TestNetwork(TestCase):

    def test_network(self):
        nw = hark.networking.Network()

        assert nw.get_host_address() == '192.168.168.1'

        assert nw.get_free_address() == '192.168.168.2'

        exclude = ['192.168.168.2']
        assert nw.get_free_address(exclude=exclude) == '192.168.168.3'

        exclude = ['192.168.168.2', '192.168.168.4']
        assert nw.get_free_address(exclude=exclude) == '192.168.168.3'

        exclude = nw.hosts()[1:]
        self.assertRaises(
            hark.exceptions.NetworkFull,
            nw.get_free_address, exclude=exclude)
