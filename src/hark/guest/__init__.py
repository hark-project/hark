from hark.exceptions import UnknownGuestException
from hark.networking import Network

_setupScriptTmpl_Debian = """#!/bin/sh
set -ex

sudo sh -c "echo '{name}' > /etc/hostname"
sudo sh -c "echo '{name}' > /etc/mailname"
sudo hostname -F /etc/hostname

# networking
cat > /tmp/hark-interfaces-tmp <<EOF
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto eth0
iface eth0 inet dhcp

# The private or host-only interface
auto eth1
iface eth1 inet static
    address {private_addr}
    netmask 255.255.255.0
EOF

# put the new file in place and restart the network
sudo mv /tmp/hark-interfaces-tmp /etc/network/interfaces
sudo /etc/init.d/networking restart
"""


class GuestConfig(object):
    def __init__(
            self,
            setup_script_template, virtualbox_os_type):
        self.setup_script_template = setup_script_template
        self._virtualbox_os_type = virtualbox_os_type

    def setup_script(self, machine, private_interface):
        ntwk = Network()
        ctx = {}
        ctx.update(machine)
        ctx['private_addr'] = private_interface['addr']
        ctx['host_addr'] = ntwk.get_host_address()
        return self.setup_script_template.format(**ctx)

    def virtualbox_os_type(self):
        return self._virtualbox_os_type

_guests = {
    'Debian-8': GuestConfig(_setupScriptTmpl_Debian, 'Debian_64'),
}


def guest_config(guest):
    if guest not in _guests:
        raise UnknownGuestException(guest)
    return _guests[guest]


def guests():
    return list(_guests.keys())
