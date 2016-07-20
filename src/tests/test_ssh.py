import os
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import hark.models.machine
import hark.models.port_mapping
import hark.exceptions
from hark.lib.command import Result
import hark.ssh


class TestHarkSSHKeys(unittest.TestCase):

    def test_hark_ssh_keys(self):
        private, public = hark.ssh.hark_ssh_keys()
        assert private.endswith('hark')
        assert public.endswith('hark.pub')
        assert os.path.exists(private)
        assert os.path.exists(public)


class TestCheckSSH(unittest.TestCase):

    @patch('hark.ssh.RemoteShellCommand.run')
    def test_check_ssh(self, mockRun):
        mockRun.return_value = Result('', 0, b'', b'')
        assert hark.ssh.check_ssh(22, 'hark')

        mockRun.return_value = Result('', 1, b'', b'')
        assert not hark.ssh.check_ssh(22, 'hark')


class TestRemoteShellCommand(unittest.TestCase):

    def test_remote_shell_command(self):
        script = "ls /; echo 'hi!'"
        cmd = hark.ssh.RemoteShellCommand(script, 2222)
        assert cmd.stdin == script
        assert cmd.cmd[0] == 'ssh'


class TestInterativeSSHCommand(unittest.TestCase):

    @patch('hark.lib.command.TerminalCommand.__init__')
    def test_ssh_command(self, mockTerminalCommandInit):
        cmd = hark.ssh.InterativeSSHCommand(22)
        priv, _ = hark.ssh.hark_ssh_keys()
        expect = [
            'ssh', '-p', '22',
            '-o', 'StrictHostKeyChecking=no',
            '-i', priv,
            'hark@localhost'
        ]
        mockTerminalCommandInit.assert_called_with(
                cmd, expect)

    @patch('hark.lib.platform.platform')
    def test_ssh_command_windows(self, mockPlatform):
        mockPlatform.return_value = 'win32'
        self.assertRaises(
            hark.exceptions.NotImplemented,
            hark.ssh.InterativeSSHCommand, 22)


class TestSSHConfig(unittest.TestCase):

    def test_ssh_conf(self):
        machine = hark.models.machine.Machine(
            name='blaerblo')
        port_mapping = hark.models.port_mapping.PortMapping(
            name='ssh', guest_port=22, host_port=57890
        )

        conf = hark.ssh.SSHConfig(machine, port_mapping)
        lines = list(str(conf).splitlines())

        assert len(lines) == 11
        assert lines[0] == 'Host blaerblo'
        assert lines[1][4:] == 'HostName 127.0.0.1'
        assert lines[2][4:] == 'User hark'
        assert lines[3][4:] == 'Port 57890'
        assert lines[4][4:] == 'UserKnownHostsFile /dev/null'
        assert lines[5][4:] == 'StrictHostKeyChecking no'
        assert lines[6][4:] == 'PasswordAuthentication no'
        assert lines[7][4:].startswith('IdentityFile')
        assert 'hark/ssh/keys/hark' in lines[7]
        assert lines[8][4:] == 'IdentitiesOnly yes'
        assert lines[9][4:] == 'LogLevel FATAL'
        assert lines[10][4:] == 'ForwardAgent no'

        conf = hark.ssh.SSHConfig(machine, port_mapping, forward_agent=True)
        lines = list(str(conf).splitlines())
        assert lines[10][4:] == 'ForwardAgent yes'
