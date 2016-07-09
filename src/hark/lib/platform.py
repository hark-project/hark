import multiprocessing
import re
import sys

from hark.exceptions import UnknownPlatformException


def platform():
    return sys.platform


def isWindows():
    return platform().startswith('win')


_platformSupport = {
    r'^darwin$': ['virtualbox'],
    r'^linux2$': ['qemu', 'virtualbox'],
    r'^win32$': ['virtualbox'],
    r'^freebsd\d+$':  ['virtualbox'],
}


def supports(driver: str) -> bool:
    pl = platform()
    for k, v in _platformSupport.items():
        if not re.match(k, pl):
            continue

        return driver in v

    raise UnknownPlatformException(pl)


def cpu_cores():
    return multiprocessing.cpu_count()
