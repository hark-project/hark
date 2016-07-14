import os
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

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
                cmd, *expect)

    @patch('hark.lib.platform.platform')
    def test_ssh_command_windows(self, mockPlatform):
        mockPlatform.return_value = 'win32'
        self.assertRaises(
            hark.exceptions.NotImplemented,
            hark.ssh.InterativeSSHCommand, 22)
