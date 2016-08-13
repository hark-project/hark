import hark.driver
import hark.exceptions
import hark.ssh
import hark.util

from hark.models.network_interface import NetworkInterface
from hark.models.port_mapping import PortMapping


class Abort(Exception):
    pass


class Procedure(object):
    """
    A hark procedure encapsulates a set of operations on different hark
    resources.

    Procedures must all have a run() method to run the procedure. After run()
    has been called, callers can use messages() to get a list of (level, msg)
    tuples.
    """
    def __init__(self, client):
        self.client = client
        self._lines = []

    def info(self, msg):
        self._lines.append(('info', msg))

    def error(self, msg):
        self._lines.append(('error', msg))

    def messages(self):
        return self._lines


class MachineProcedure(Procedure):
    """
    Procedures which operate upon machines.
    """
    def __init__(self, client, machine):
        Procedure.__init__(self, client)
        self.machine = machine

    def driver(self):
        """Get the driver instance for this machine"""
        return hark.driver.get_driver(self.machine['driver'], self.machine)


class NewMachine(MachineProcedure):
    """
    A procedure for creating a new machine.
    """

    def __init__(self, client, machine):
        MachineProcedure.__init__(self, client, machine)

        self.ssh_port_mapping = None
        self.private_interface = None

    def run(self):
        try:
            image, baseImagePath = self.image()
        except hark.exceptions.ImageNotFound as e:
            self.error('Image not found locally: %s' % e)
            self.error("Run 'hark image pull' to download it first.")
            raise Abort

        # Get a driver for this machine
        try:
            # Save it in the DAL.
            # This will identify duplicates before we attempt to create the
            # machine.
            self.saveMachineToDal()
        except hark.exceptions.DuplicateModelException:
            self.error(
                'Machine already exists with these options:\n\t%s' %
                self.machine)
            raise Abort

        self.driver().create(baseImagePath, self.client.dal())

        self.createPortMapping()

        self.configureNetwork()

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

    def configureNetwork(self):
        # We need to assign a static IP address for the host-only interface.
        free_addr = self.client.freePrivateIP()
        iface = NetworkInterface(
            machine_id=self.machine['machine_id'],
            kind='private',
            addr=free_addr)

        self.client.createNetworkInterface(iface)

        self.private_interface = iface


class DestroyMachine(MachineProcedure):
    def run(self):
        from hark.driver.status import PAUSED, RUNNING, STOPPED
        d = self.driver()

        s = d.status()
        if s in (PAUSED, RUNNING):
            self.info("Machine status is '%s' - stopping it first." % s)
            d.stop()
            d.waitStatus(STOPPED)

        # destroy the VM in the driver
        d.destroy()

        # now delete it from the DB
        self.client.deleteMachine(self.machine)
