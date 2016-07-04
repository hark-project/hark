import re
from typing import List

from .. import base
from hark.lib.command import Command, Result
from hark.models.port_mapping import PortMapping
import hark.log as log


class Driver(base.BaseDriver):
    cmd = 'VBoxManage'
    versionArg = '-v'

    def _run(self, cmd):
        cmd.insert(0, self.cmd)
        return Command(*cmd).assertRun()

    def create(self, baseImagePath):
        log.debug("virtualbox: Creating machine '%s'", self._name())
        log.debug("virtualbox: base image will be '%s'", baseImagePath)
        cmds = self._createCommands(baseImagePath)
        for cmd in cmds:
            self._run(cmd)

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

    def setPortMappings(self, mappings: List[PortMapping]) -> None:
        for pm in mappings:
            fpm = pm.format_virtualbox()
            cmd = self._modifyvm('--natpf1', fpm)
            self._run(cmd)

    def _createCommands(self, baseImagePath: str) -> List[List[str]]:
        name = self._name()
        mod = self._modifyvm
        cmds = (
            ['createvm', '--name', name,   '--register'],

            # TODO(cera)
            # mod('--ostype', self.machine.os_type()),

            mod('--acpi', 'on'),
            mod('--ioapic', 'on'),
            mod('--memory', str(self.machine['memory_mb'])),

            mod('--nic1', 'nat'),
            # TODO(cera)

            mod(
                '--nic2', 'hostonly',
                '--hostonlyadapter2', self._host_only_interface()),

            mod('--nictype1', 'virtio'),
            mod('--nictype2', 'virtio'),

            ['storagectl', name, '--name', 'IDE Controller', '--add', 'ide'],
            [
                'storageattach', name, '--storagectl', 'IDE Controller',
                '--port', '0',
                '--device', '0',
                '--type', 'hdd',
                '--medium', baseImagePath,

                # --mtype tells virtualbox to copy-on-write from the base image
                # instead of mutating it
                '--mtype', 'multiattach'
            ],
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
