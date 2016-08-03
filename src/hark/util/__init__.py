import socket

from hark.exceptions import ImageNotFound


def getFreePort(exclude=[]):
    "Find a free port to bind to. Exclude anything from the list provided."
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
