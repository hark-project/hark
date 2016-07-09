

_drivers = ['virtualbox', 'qemu']


def drivers():
    return _drivers


def get_driver(name, machine):
    import hark.lib.platform
    from hark.exceptions import (
        UnknownDriverException, UnsupportedDriverException
    )
    from . import virtualbox

    if name not in _drivers:
        raise UnknownDriverException(name)

    if not hark.lib.platform.supports(name):
        raise UnsupportedDriverException(hark.lib.platform.platform(), name)

    if name == 'virtualbox':
        return virtualbox.Driver(machine)
