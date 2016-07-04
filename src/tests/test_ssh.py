import os
import unittest
from unittest.mock import patch

import hark.ssh


class TestHarkSSHKeys(unittest.TestCase):

    def test_hark_ssh_keys(self):
        private, public = hark.ssh.hark_ssh_keys()
        assert private.endswith('hark')
        assert public.endswith('hark.pub')
        assert os.path.exists(private)
        assert os.path.exists(public)


class TestRemoteShellCommand(unittest.TestCase):

    def test_remote_shell_command(self):
        script = "ls /; echo 'hi!'"
        cmd = hark.ssh.RemoteShellCommand(script, 2222)
        assert cmd.stdin == script
        assert 'ssh' in cmd.cmd


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
