from hark.exceptions import UnknownGuestException

_setupScriptTmpl_Debian = """#!/bin/sh
set -ex
sudo sh -c "echo '{name}' > /etc/hostname"
sudo sh -c "echo '{name}' > /etc/mailname"
sudo hostname -F /etc/hostname
"""


class GuestConfig(object):
    def __init__(
               self,
               setup_script_template,
               virtualbox_os_type):
        self.setup_script_template = setup_script_template
        self._virtualbox_os_type = virtualbox_os_type

    def setup_script(self, machine):
        return self.setup_script_template.format(**machine)

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
