import re

import hark.exceptions
from hark.lib.command import Command
import hark.log as log
import hark.models.config
import hark.networking

from .. import base
from .. import status


HOST_ONLY_INTERFACE_CFG_KEY = 'virtualbox_host_only_interface'


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

    def create(self, baseImagePath, dal):
        """
        Create a new image.

        A DAL instance is needed in case the driver needs to persist some
        global configuration.
        """
        hostonly_interface_name = self.host_only_interface(dal)

        log.debug("virtualbox: Creating machine '%s'", self._name())
        log.debug("virtualbox: base image will be '%s'", baseImagePath)
        cmds = self._createCommands(hostonly_interface_name)
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
        attachCommand = attachCommand[:len(attachCommand) - 2]
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

    def _createCommands(self, host_only_interface):
        name = self._name()
        mod = self._modifyvm
        cmds = (
            ['createvm', '--name', name, '--register'],

            mod('--ostype', self.guest_config.virtualbox_os_type()),

            mod('--acpi', 'on'),
            mod('--ioapic', 'on'),
            mod('--memory', str(self.machine['memory_mb'])),

            mod('--nic1', 'nat'),
            mod(
                '--nic2', 'hostonly',
                '--hostonlyadapter2', host_only_interface),

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

    def host_only_interface(self, dal):
        """
        Return the name of the hark-dedicated host only interface. Create one
        if necessary.
        """
        interfaceCfg = dal.read(hark.models.config.Config, constraints={
            'name': HOST_ONLY_INTERFACE_CFG_KEY
        })
        if not len(interfaceCfg):
            # no host-only interface name is recorded by the config - create
            # one and save it.
            hostonly_interface_name = self._create_host_only_interface()
            model = hark.models.config.Config(
                name=HOST_ONLY_INTERFACE_CFG_KEY,
                value=hostonly_interface_name)
            dal.create(model)
            return hostonly_interface_name
        else:
            return interfaceCfg[0]['value']

    def _create_host_only_interface(self):
        "Create a host-only interface and return its name"
        cmd = ['hostonlyif', 'create']
        res = self._run(cmd)
        m = r"Interface '(.+)' was successfully created"
        matches = re.findall(m, res.stdout)
        if len(matches) == 0:
            raise Exception(
                "Could not parse output of cmd %s: '%s'", cmd, res.stdout)
        log.debug(
            'virtualbox: created new host-only interface: %s', matches[0])
        self._assign_host_only_interface_ip(matches[0])
        return matches[0]

    def _assign_host_only_interface_ip(self, name):
        network = hark.networking.Network()

        addr = network.get_host_address()

        cmd = ['hostonlyif', 'ipconfig', name, '--ip', addr]
        self._run(cmd)
        log.debug(
            'virtualbox: assigned addr %s to host-only interface %s',
            addr, name)
