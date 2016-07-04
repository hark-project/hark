from typing import List

from hark.exceptions import UnknownGuestException
from hark.models.machine import Machine

_setupScriptTmpl_Debian = """#!/bin/sh
set -ex
sudo sh -c "echo '{name}' > /etc/hostname"
sudo sh -c "echo '{name}' > /etc/mailname"
sudo hostname -F /etc/hostname
"""


class GuestConfig(object):
    def __init__(self, setup_script_template) -> None:
        self.setup_script_template = setup_script_template

    def setup_script(self, machine: Machine) -> str:
        return self.setup_script_template.format(**machine)

_guests = {
    'Debian-8': GuestConfig(_setupScriptTmpl_Debian),
}


def guest_config(guest: str) -> GuestConfig:
    if guest not in _guests:
        raise UnknownGuestException(guest)
    return _guests[guest]


def guests() -> List[str]:
    return list(_guests.keys())
