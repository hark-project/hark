import re
import sys

from hark.exceptions import UnknownPlatformException


def platform():
    return sys.platform


def isWindows():
    return platform().startswith('win')


_platformSupport = {
    re.compile(r'^darwin$'): ['virtualbox'],
    re.compile(r'^linux2$'): ['qemu', 'virtualbox'],
    re.compile(r'^win32$'): ['virtualbox'],
    re.compile(r'^freebsd\d+$'):  ['virtualbox'],
}


def supports(driver: str) -> bool:
    pl = platform()
    for k, v in _platformSupport.items():
        if not k.match(pl):
            continue

        return driver in v

    raise UnknownPlatformException(pl)
