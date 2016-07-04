import click
import io
import sys
from typing import List

import hark.driver
import hark.guest
from hark.exceptions import ImageNotFound, MachineNotFound
from hark.models import BaseModel
from hark.models.image import Image

# Set up some reusable options

_drivers = hark.driver.drivers()
driverOption = click.option(
    "--driver", type=click.Choice(_drivers),
    prompt="Choose machine driver from: %s\nDriver" % ", ".join(_drivers),
    required=True, help="The machine driver")


_guests = hark.guest.guests()
guestOption = click.option(
    "--guest", type=click.Choice(_guests),
    prompt="Choose machine guest OS from: %s\nGuest" % ", ".join(_guests),
    required=True, help="The machine guest OS")


def modelsWithHeaders(models: List[BaseModel]) -> str:
    """
    Generate a string to print a list of models with headers.
    """
    buf = io.StringIO()
    if len(models) == 0:
        return ""

    fields = models[0].fields

    # figure out what the field length should be for each field.
    # it is the greatest length of any value for that field in the list of
    # models, or the length of the field name itself; whichever is greater.
    lens = [max(len(str(m[f])) for m in models) for f in fields]
    lens = [max(l, len(fields[i])) for i, l in enumerate(lens)]

    padded = [f.ljust(l) for f, l in zip(fields, lens)]

    buf.write(click.style(" ".join(padded) + "\n", fg='magenta'))

    paddedModels = []
    for m in models:
        vals = [m[f] for f in fields]
        padded = [str(f).ljust(l) for f, l in zip(vals, lens)]
        paddedModels.append(" ".join(padded))

    buf.write("\n".join(paddedModels))
    buf.seek(0)
    return buf.read()


def findImage(images: List[Image], driver: str, guest: str) -> Image:
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


def getMachine(client, name):
    try:
        m = client.getMachine(name)
        return m
    except MachineNotFound:
        click.secho("Machine not found: " + name, fg='red')
        sys.exit(1)


def getSSHMapping(client, machine):
    mappings = client.portMappings(
        name='ssh', machine_id=machine['machine_id'])
    if len(mappings) == 0:
        click.secho(
            "Could not find any configured ssh port mapping for machine '%s'"
            % machine['name'], fg='red')
        sys.exit(1)
    return mappings[0]
