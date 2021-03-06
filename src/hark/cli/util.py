import click
import sys

import hark.driver
import hark.guest
from hark.exceptions import MachineNotFound

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


imageVersionPrompt = click.option(
    '--version', prompt='What version should this image be treated as?',
    type=int, help='The version to treat this image as')


def promptModelChoice(models):
    click.echo(modelsWithHeaders(models, add_index=True))
    while True:
        i = click.prompt('Choose by num', type=int)
        if i > 0 and i <= len(models):
            return models[i - 1]
        click.secho('Invalid choice: %d' % i, fg='red')


def modelsWithHeaders(models, add_index=False):
    """
    Generate a string to print a list of models with headers.
    """
    import io

    buf = io.StringIO()
    if len(models) == 0:
        return ""

    fields = models[0].fields

    if add_index:
        # insert the num field
        fields.insert(0, 'num')
        # copy the models so that we don't mutate
        models = [dict(m) for m in models]
        # add num to each of them
        for i, m in enumerate(models):
            m['num'] = i + 1

    # figure out what the field length should be for each field.
    # it is the greatest length of any value for that field in the list of
    # models, or the length of the field name itself; whichever is greater.
    lens = [max(len(str(m[f])) for m in models) for f in fields]
    lens = [max(l, len(fields[i])) for i, l in enumerate(lens)]

    # padded header fields
    padded = [f.ljust(l) for f, l in zip(fields, lens)]

    # write out the header
    buf.write(click.style(" ".join(padded) + "\n", fg='magenta'))

    paddedModels = []
    for m in models:
        vals = [m[f] for f in fields]

        padded = [str(f).ljust(l) for f, l in zip(vals, lens)]
        paddedModels.append(" ".join(padded))

    buf.write("\n".join(paddedModels))
    buf.seek(0)
    return buf.read()


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


def loadLocalContext(hark_home=None, context_class=None):
    if context_class is None:
        from hark.context import Context
        context_class = Context

    if hark_home is not None:
        return context_class(hark_home)
    return context_class.home()


def getPrivateInterface(client, machine):
    ifaces = client.networkInterfaces(machine=machine, kind='private')
    if not len(ifaces):
        # TODO(cera) - typed exception
        raise Exception("No private interface found")
    return ifaces[0]


def printProcedureLines(procedure):
    for level, msg in procedure.messages():
        if level == 'error':
            click.secho(msg, fg='red')
        else:
            click.echo(msg)
