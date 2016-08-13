import time

import hark.guest
import hark.log
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

    def assertStatus(self, msg, *valid_statuses):
        """
        Given a machine driver instance, throw hark.exceptions.InvalidStatus
        unless the status of the machine is in the specified set.

        msg is a message which will be used to format the exception.
        """
        s = self.status()

        if s not in valid_statuses:
            fmt = ', '.join(["'%s'" % str(st) for st in valid_statuses])
            raise hark.exceptions.InvalidStatus(
                "cannot remove a machine unless it's stopped: "
                "status is '%s' and needs to be one of (%s)" % (s, fmt))

    def waitStatus(self, status, interval_ms=1000):
        hark.log.info('Waiting for machine %s status to be %s' % (
            self.machine['name'], status))
        while True:
            if self.status() == status:
                return
            time.sleep(interval_ms / 1000)
