from hark.exceptions import BadHarkEnvironment, ImageNotFound


def getFreePort(exclude=[]):
    "Find a free port to bind to. Exclude anything from the list provided."
    import socket
    while True:
        sock = socket.socket()
        sock.bind(('', 0))
        _, port = sock.getsockname()
        sock.close()

        if port not in exclude:
            return port


def findImage(images, driver, guest):
    """
    Given a list of images, find the highest-version image for this driver and
    guest.

    Raises ImageNotFound if none is found.
    """
    im = [i for i in images if i['driver'] == driver and i['guest'] == guest]
    if len(im) == 0:
        raise ImageNotFound(
            "no local image for driver '%s' and guest: '%s'" % (driver, guest))
    return im[-1]


def checkHarkEnv():
    """
    Check that the process and system environment is appropriate for running
    hark.
    """
    import getpass
    import sys

    if getpass.getuser() == 'root':
        raise BadHarkEnvironment('hark cannot be run as root, or with sudo')

    if sys.version_info.major == 2:
        raise BadHarkEnvironment(
            'hark is not supported on python2; you are running %d.%d.%d' %
            (
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro))
