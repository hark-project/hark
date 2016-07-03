from hark.exceptions import UnknownDriverException

from . import virtualbox

_drivers = {
        'virtualbox': virtualbox.Driver,
        'qemu': None,
}


def drivers():
    return list(_drivers.keys())


def get_driver(name, machine):
    if name not in _drivers:
        raise UnknownDriverException(name)

    return _drivers[name](machine)
