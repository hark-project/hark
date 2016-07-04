import click
import sys

from hark.cli.util import (
    driverOption, guestOption,
    modelsWithHeaders,
    getMachine, getSSHMapping,
)
from hark.client import LocalClient
from hark.context import Context
import hark.driver
import hark.guest
import hark.exceptions
import hark.log as logger
from hark.models.machine import MEMORY_MINIMUM
import hark.ssh
import hark.util


@click.group(name='hark')
@click.pass_context
@click.option('--hark-home', envvar='HARKHOME', type=str)
@click.option('--log-level', envvar='LOGLEVEL', type=str, default='INFO')
def hark_main(ctx, hark_home=None, log_level='INFO'):
    "Hark is a tool to help manage virtual machines"
    logger.setLevel(log_level)

    if hark_home is not None:
        harkctx = Context(hark_home)
    else:
        harkctx = Context.home()

    logger.setOutputFile(harkctx.log_file())

    ctx.obj = LocalClient(harkctx)


@hark_main.group()
@click.pass_obj
def vm(client):
    "Commands for working with hark machines"
    pass


@vm.command(name='list')
@click.pass_obj
def machine_list(client):
    "List hark machines"
    machines = client.machines()

    click.secho("vm list: found %d hark machines" % len(machines), fg='green')
    click.echo(modelsWithHeaders(machines))


@vm.command()
@click.pass_obj
@click.option(
    "--name", type=str,
    prompt="New machine name", help="The name of the machine")
@driverOption
@guestOption
@click.option(
    "--memory_mb", type=click.IntRange(MEMORY_MINIMUM),
    prompt="Memory (MB)", help="Memory allocated to the machine in MB")
def new(client, **kwargs):
    "Create a new hark machine"
    from hark.cli.util import findImage
    from hark.models.machine import Machine
    from hark.models.port_mapping import PortMapping

    # Create and validate the machine model.
    m = Machine.new(**{f: kwargs[f] for f in Machine.fields if f in kwargs})
    m.validate()

    # See if we have the specified image
    try:
        image = findImage(client.images(), kwargs['driver'], kwargs['guest'])
        baseImagePath = client.imagePath(image)
    except hark.exceptions.ImageNotFound as e:
        # TODO(cera) - don't just fail here
        click.secho('Image not found locally: %s' % e, fg='red')
        sys.exit(1)

    # Get a driver for this machine
    d = hark.driver.get_driver(kwargs['driver'], m)

    # Save it in the DAL.
    # This will identify duplicates before we attempt to create the machine.
    try:
        client.createMachine(m)
    except hark.exceptions.DuplicateModelException:
        click.secho(
            'Machine already exists with these options:\n\t%s' % kwargs,
            fg='red')
        sys.exit(1)

    # Create the machine
    click.secho('Creating machine:', fg='green')
    click.echo(m.json(indent=4))
    d.create(baseImagePath)

    # Set up an SSH port mapping for this machine
    # We need to find a free port that is not used by any other machines.
    mappings = client.portMappings()
    used_host_ports = [mp['host_port'] for mp in mappings]
    host_port = hark.util.get_free_port(exclude=used_host_ports)
    guest_port = 22
    mapping = PortMapping(
        host_port=host_port,
        guest_port=guest_port,
        machine_id=m['machine_id'],
        name='ssh')

    click.secho('Configuring ssh port mapping:', fg='green')
    click.echo(mapping.json(indent=4))

    # Create the mapping in the driver
    d.setPortMappings([mapping])

    # Save the mapping in the DAL
    client.createPortMapping(mapping)


@vm.command()
@click.pass_obj
@click.option(
    "--name", type=str,
    prompt="Machine name", help="The name of the machine")
def setup(client, name):
    "Run the setup script for a machine"
    m = getMachine(client, name)
    setup_script = hark.guest.guest_config(m['guest']).setup_script(m)
    mapping = getSSHMapping(client, m)
    click.secho(
        "Running machine setup script for '%s'" % name, fg='green')
    cmd = hark.ssh.RemoteShellCommand(setup_script, mapping['host_port'])
    cmd.assertRun()
    click.secho('Done.', fg='green')


@vm.command()
@click.pass_obj
@click.option(
    "--name", type=str,
    prompt="Machine name", help="The name of the machine")
@click.option(
    "--gui", is_flag=True, default=False,
    help='Whether to start with a gui')
def start(client, name, gui):
    "Start a machine"

    m = getMachine(client, name)

    click.echo('Starting machine: ' + name)

    d = hark.driver.get_driver(m['driver'], m)

    d.start(gui=gui)
    click.secho('Done.', fg='green')
    click.secho(
        "Run 'hark ssh --name %s' to connect to the machine" % name,
        fg='green')


@vm.command()
@click.pass_obj
@click.option(
    "--name", type=str,
    prompt="Machine name", help="The name of the machine")
def stop(client, name):
    "Stop a machine"

    m = getMachine(client, name)

    click.echo('Stopping machine: ' + name)

    d = hark.driver.get_driver(m['driver'], m)

    d.stop()
    click.secho('Done.', fg='green')


@vm.command()
@click.pass_obj
def mappings(client):
    "Show all configured port mappings"

    mappings = client.portMappings()
    click.secho(
        "vm mappings: found %d configured port mappings" % len(mappings),
        fg='green')
    click.echo(modelsWithHeaders(mappings))


@hark_main.command()
@click.pass_obj
def log(client):
    "Show the hark log"
    for line in client.log().splitlines():
        click.echo(line)


@hark_main.group()
@click.pass_obj
def image(client):
    "Work with hark images"
    pass


@image.command()
@click.pass_obj
@driverOption
@guestOption
@click.option(
    '--local-file', default=None, type=str,
    help='Local file to pull from instead of remote image store service')
def pull(client, driver=None, guest=None, local_file=None):
    "Pull down an image for the local cache"
    import hark.exceptions
    import hark.models.image

    if local_file is None:
        # TODO(cera) - Implement reading from the remote image store.
        raise hark.exceptions.NotImplemented

    version = click.prompt(
        "What version should this image be treated as?", type=int)

    image = hark.models.image.Image(
        driver=driver, guest=guest, version=version)
    client.saveImageFromFile(image, local_file)


@image.command(name='list')
@click.pass_obj
def image_list(client):
    images = client.images()
    click.secho(
        "image list: found %d cached hark images" % len(images), fg='green')
    click.echo(modelsWithHeaders(images))


@hark_main.command()
@click.pass_obj
@click.option(
    "--name", type=str, required=True,
    prompt="Machine name", help="The name of the machine")
def ssh(client, name=None):
    "Connect to a machine over SSH"
    m = getMachine(client, name)

    mapping = getSSHMapping(client, m)

    cmd = hark.ssh.InterativeSSHCommand(mapping['host_port'])
    cmd.run()

if __name__ == '__main__':
    hark_main()
