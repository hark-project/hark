import ipaddress

from hark.exceptions import NetworkFull


DEFAULT_NETWORK = '192.168.168.0/24'


class Network(object):
    """
    The Network class represents the hark network.

    Hark gives all hosts a static IP in a private /24. The DEFAULT_NETWORK
    value is chosen based the relative unlikelihood of it being in use in the
    wild, at least in the networks of hark users.
    """

    def __init__(self, network=DEFAULT_NETWORK):
        self.network = ipaddress.ip_network(network)

    def hosts(self):
        return [str(h) for h in self.network.hosts()]

    def get_host_address(self):
        return self.hosts()[0]

    def get_free_address(self, exclude=[]):
        """
        Given a list of hosts to exclude - implicitly, addresses that have
        already been assigned - return an available free IP address.
        """
        all_hosts = self.hosts()[1:]

        available = [h for h in all_hosts if h not in exclude]

        if len(available):
            return available[0]
        else:
            raise NetworkFull(len(all_hosts))
