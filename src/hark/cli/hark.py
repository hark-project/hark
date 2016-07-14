from __future__ import absolute_import  # 2-3 compat

import click

from hark.cli.util import (
    driverOption, guestOption, imageVersionPrompt,
    findImage,
    modelsWithHeaders, promptModelChoice,
    getMachine, getSSHMapping,
    loadLocalContext,
)
from hark.models.machine import MEMORY_MINIMUM
from hark.imagestore import DEFAULT_IMAGESTORE_URL


@click.group(name='hark')
@click.pass_context
@click.option('--hark-home', envvar='HARKHOME', type=str)
@click.option('--log-level', envvar='LOGLEVEL', type=str, default='INFO')
def hark_main(ctx, hark_home=None, log_level='INFO'):
    "Hark is a tool to help manage virtual machines"
    from hark.client import LocalClient
    import hark.log

    hark.log.setLevel(log_level)

    harkctx = loadLocalContext(hark_home)

    hark.log.setOutputFile(harkctx.log_file())

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
@click.pass_context
@click.option(
    "--name", type=str,
    prompt="New machine name", help="The name of the machine")
@driverOption
@guestOption
@click.option(
    "--memory_mb", type=click.IntRange(MEMORY_MINIMUM),
    prompt="Memory (MB)", help="Memory allocated to the machine in MB")
def new(ctx, **kwargs):
    "Create a new hark machine"
    import hark.driver
    import hark.exceptions
    from hark.models.port_mapping import PortMapping
    from hark.models.machine import Machine
    import hark.ssh
    import hark.util

    import time

    client = ctx.obj

    # Create and validate the machine model.
    m = Machine.new(**{f: kwargs[f] for f in Machine.fields if f in kwargs})
    m.validate()

    # See if we have the specified image
    try:
        image = findImage(client.images(), kwargs['driver'], kwargs['guest'])
        baseImagePath = client.imagePath(image)
    except hark.exceptions.ImageNotFound as e:
        click.secho('Image not found locally: %s' % e, fg='red')
        click.secho("Run 'hark image pull' to download it first.", fg='red')
        raise click.Abort

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
        raise hark.Aborted

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

    # Now wait until the machine is running and run the setup script
    click.secho('Done.', fg='green')

    if not click.confirm('Start the machine and run the setup script?'):
        click.secho(
            'You should run the setup script manually when you start '
            'the machine, with these commands:', fg='red')
        click.secho('\thark vm start --name %s' % m['name'])
        click.secho('\thark vm setup --name %s' % m['name'])
        return

    ctx.invoke(start, name=m['name'], gui=False)
    click.secho("Waiting for SSH to be available", fg='green')
    while True:
        click.secho('.', fg='green')
        time.sleep(1)
        if hark.ssh.check_ssh(host_port):
            break
    ctx.invoke(setup, name=m['name'])


@vm.command()
@click.pass_obj
@click.option(
    "--name", type=str,
    prompt="Machine name", help="The name of the machine")
def setup(client, name):
    "Run the setup script for a machine"
    import hark.guest
    import hark.ssh

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
    import hark.driver

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
    import hark.driver

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


@image.command(name='pull')
@click.pass_obj
@click.option(
    '--imagestore-url', type=str,
    envvar='IMAGESTORE_URL', default=DEFAULT_IMAGESTORE_URL)
def image_pull(client, imagestore_url=None):
    "Pull down an image for the local cache"
    from hark.client import ImagestoreClient

    image_client = ImagestoreClient(imagestore_url)

    image = promptModelChoice(image_client.images())

    if image in client.images():
        click.secho(
            'Already have this image locally: %s' % image.json(), fg='red')
        click.secho(
            "To download it again, first run 'hark image remove'",
            fg='red')
        return

    url = image_client.image_url(image)

    click.secho('Downloading image: ' + image.json(), fg='green')
    click.secho('From URL: %s' % url, fg='green')

    client.saveImageFromUrl(image, url)

    return


@image.command(name='pull-local')
@click.pass_obj
@click.argument('local_file', type=str)
@driverOption
@guestOption
@imageVersionPrompt
def image_pull_local(client, local_file, driver, guest, version):
    "Save an image from a local file"
    from hark.models.image import Image
    image = Image(
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
    import hark.driver
    from hark.driver.status import RUNNING
    import hark.ssh

    m = getMachine(client, name)
    d = hark.driver.get_driver(m['driver'], m)
    mapping = getSSHMapping(client, m)

    status = d.status()

    if status != RUNNING:
        click.secho(
            "Cannot SSH: Machine status is '%s', needs to be '%s'"
            % (status, RUNNING), fg='red')
        click.secho(
            "Try starting the machine first with 'hark vm start'", fg='red')
        raise hark.Aborted

    cmd = hark.ssh.InterativeSSHCommand(mapping['host_port'])
    cmd.run()

if __name__ == '__main__':
    hark_main()
