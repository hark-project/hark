import re

import hark.exceptions
from hark.lib.command import Command
import hark.log as log

from .. import base
from .. import status


class Driver(base.BaseDriver):
    cmd = 'VBoxManage'
    versionArg = '-v'

    def _run(self, cmd):
        # copy the list before mutating it
        cmd = list(cmd)
        # insert the binary name
        cmd.insert(0, self.cmd)
        # run it
        return Command(cmd).assertRun()

    def status(self):
        state = self._vmInfo()['VMState']
        if state == 'running':
            return status.RUNNING
        elif state == 'poweroff':
            return status.STOPPED
        elif state == 'aborted':
            return status.ABORTED
        elif state == 'paused':
            return status.PAUSED
        else:
            raise hark.exceptions.UnrecognisedMachineState(state)

    def _vmInfo(self):
        res = self._run(['showvminfo', self._name(), '--machinereadable'])
        vmInfo = {}
        for line in res.stdout.splitlines():
            k, v = line.split("=", 1)
            vmInfo[k] = v.strip('"')
        return vmInfo

    def create(self, baseImagePath):
        log.debug("virtualbox: Creating machine '%s'", self._name())
        log.debug("virtualbox: base image will be '%s'", baseImagePath)
        cmds = self._createCommands()
        for cmd in cmds:
            self._run(cmd)
        self._attachStorage(baseImagePath)

    def _attachStorage(self, baseImagePath):
        name = self._name()
        self._run([
            'storagectl', name, '--name', 'sata1', '--add', 'sata'
        ])
        attachCommand = [
            'storageattach', name, '--storagectl', 'sata1',
            '--port', '0',
            '--device', '0',
            '--type', 'hdd',
            '--medium', baseImagePath,
            '--mtype', 'multiattach',
        ]
        try:
            self._run(attachCommand)
        except hark.exceptions.CommandFailed as e:
            # If we get an error saying the medium is locked for reading by
            # another task, it means that we don't need to specify multiattach
            # - it's only actually required the first time we attach this
            # medium to a machine.
            stderr = e.result.stderr
            if 'is locked for reading by another task' not in stderr:
                raise e
        else:
            return

        # remove the last two arguments and try again
        attachCommand = attachCommand[:len(attachCommand)-2]
        self._run(attachCommand)

    def _name(self):
        return self.machine['name']

    def start(self, gui=False):
        log.debug("virtualbox: Starting machine '%s'", self._name())

        if gui:
            uiType = 'gui'
        else:
            uiType = 'headless'

        cmd = ['startvm', self._name(), '--type', uiType]
        self._run(cmd)

    def stop(self):
        log.debug("virtualbox: Stopping machine '%s'", self._name())
        cmd = self._controlvm('acpipowerbutton')
        self._run(cmd)

    def setPortMappings(self, mappings):
        for pm in mappings:
            fpm = pm.format_virtualbox()
            cmd = self._modifyvm('--natpf1', fpm)
            self._run(cmd)

    def _createCommands(self):
        name = self._name()
        mod = self._modifyvm
        cmds = (
            ['createvm', '--name', name,   '--register'],

            mod('--ostype', self.guest_config.virtualbox_os_type()),

            mod('--acpi', 'on'),
            mod('--ioapic', 'on'),
            mod('--memory', str(self.machine['memory_mb'])),

            mod('--nic1', 'nat'),
            mod(
                '--nic2', 'hostonly',
                '--hostonlyadapter2', self._host_only_interface()),

            mod('--nictype1', 'virtio'),
            mod('--nictype2', 'virtio'),

        )

        return cmds

    def _modifyvm(self, prop, *val):
        c = ['modifyvm', self.machine['name'], prop]
        c.extend(val)
        return c

    def _controlvm(self, *val):
        c = ['controlvm', self.machine['name']]
        c.extend(val)
        return c

    def _host_only_interface(self):
        cmd = ['list', 'hostonlyifs']
        res = self._run(cmd)
        names = [
            l for l in res.stdout.splitlines()
            if l.startswith("Name:")
        ]
        if len(names) == 0:
            # Create one
            return self._create_host_only_interface()
        return names[0].split("Name:")[1].strip()

    def _create_host_only_interface(self):
        cmd = ['hostonlyif', 'create']
        res = self._run(cmd)
        m = r".+\nInterface '(.+)' was successfully created"
        matches = re.findall(m, res.stdout)
        if len(matches) == 0:
            raise Exception(
                "Could not parse output of cmd %s: '%s'", cmd, res.stdout)
        return matches[0]
