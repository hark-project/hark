import hark.guest
from hark.lib.command import which, Command


class BaseDriver(object):

    def __init__(self, machine):
        self.machine = machine
        self.guest_config = hark.guest.guest_config(machine['guest'])

    @classmethod
    def commandPath(cls):
        # subclass is expected to set cmd
        return which(cls.cmd)

    @classmethod
    def isAvailable(cls):
        return cls.commandPath() is not None

    @classmethod
    def version(cls):
        cmd = Command(cls.cmd, cls.versionArg)
        res = cmd.assertRun()
        return res.stdout.strip()
