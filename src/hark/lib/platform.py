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
    r'^linux\d?$': ['qemu', 'virtualbox'],
    r'^win32$': ['virtualbox'],
    r'^freebsd\d+$':  ['virtualbox'],
}


def supports(driver):
    pl = platform()
    for k, v in _platformSupport.items():
        if not re.match(k, pl):
            continue

        return driver in v

    raise UnknownPlatformException(pl)


def cpu_cores():
    return multiprocessing.cpu_count()
