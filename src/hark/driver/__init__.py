import hark.lib.platform
from hark.exceptions import (
    UnknownDriverException, UnsupportedDriverException
)

from . import virtualbox


_drivers = {
    'virtualbox': virtualbox.Driver,
    'qemu': None,  # TODO(cera)
}


def drivers():
    return list(_drivers.keys())


def get_driver(name, machine):
    if name not in _drivers:
        raise UnknownDriverException(name)

    if not hark.lib.platform.supports(name):
        raise UnsupportedDriverException(hark.lib.platform.platform(), name)

    return _drivers[name](machine)
