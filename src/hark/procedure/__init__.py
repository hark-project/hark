import hark.driver
import hark.exceptions
import hark.ssh
import hark.util

from hark.models.port_mapping import PortMapping


class Abort(Exception):
    pass


class Procedure(object):
    """
    A hark procedure encapsulates a set of operations on different hark
    resources.

    A procedure's run() method is a generator which yields lies that can be
    printed to the console or some other UI.
    """

    def __init__(self, client):
        self.client = client


class NewMachine(Procedure):
    def __init__(self, client, machine):
        Procedure.__init__(self, client)
        self.machine = machine

        self.ssh_port_mapping = None
        self.private_interface = None

    def run(self):
        try:
            image, baseImagePath = self.image()
        except hark.exceptions.ImageNotFound as e:
            yield 'Image not found locally: %s' % e
            yield "Run 'hark image pull' to download it first."
            raise Abort

        # Get a driver for this machine
        try:
            # Save it in the DAL.
            # This will identify duplicates before we attempt to create the
            # machine.
            self.saveMachineToDal()
        except hark.exceptions.DuplicateModelException:
            yield 'Machine already exists with these options:\n\t%s' % \
                self.machine
            raise Abort

        self.driver().create(baseImagePath)

        self.createPortMapping()

    def image(self):
        """
        Check for the image specified by this machine. Return a tuple of
        (image, baseImagePath).
        """
        image = hark.util.findImage(
                self.client.images(),
                self.machine['driver'], self.machine['guest'])
        baseImagePath = self.client.imagePath(image)
        return image, baseImagePath

    def driver(self):
        """Get the driver for the machine to be built"""
        return hark.driver.get_driver(self.machine['driver'], self.machine)

    def saveMachineToDal(self):
        self.client.createMachine(self.machine)

    def createPortMapping(self):
        """Set up an SSH port mapping for this machine."""

        # We need to find a free port that is not used by any other machines.
        mappings = self.client.portMappings()
        used_host_ports = [mp['host_port'] for mp in mappings]
        host_port = hark.util.getFreePort(exclude=used_host_ports)
        guest_port = 22
        mapping = PortMapping(
            host_port=host_port,
            guest_port=guest_port,
            machine_id=self.machine['machine_id'],
            name='ssh')

        self.ssh_port_mapping = mapping

        # Create the mapping in the driver
        self.driver().setPortMappings([mapping])

        # Save the mapping in the DAL
        self.client.createPortMapping(mapping)


class MachineSetup(Procedure):
    def __init__(self, client, machine):
        Procedure.__init__(self, client)
        self.machine = machine

    def run(self):
        pass
