import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import hark.exceptions
from hark.lib.command import which, Command, Result, TerminalCommand


class TestWhich(unittest.TestCase):
    def test_which(self):
        expect = ('/bin/true', '/usr/bin/true')

        path = which('true')
        assert path in expect

        path = which('fhdljhfdjdfkljsd')
        assert path is None

    @patch('hark.lib.platform.platform')
    def test_which_windows(self, mockPlatform):
        mockPlatform.return_value = 'win32'
        self.assertRaises(
            hark.exceptions.NotImplemented,
            which, 'true')


class TestCommand(unittest.TestCase):
    def test_command_result_true_false(self):
        for c, status in (("true", 0), ("false", 1)):
            command = Command([c])

            res = command.run()
            assert isinstance(res, Result)
            assert res.exit_status == status
            assert len(res.stdout) == 0
            assert len(res.stderr) == 0

    def test_command_output(self):
        word = "blaaaa"
        c = Command(["echo", word])

        res = c.run()
        assert res.stdout.strip() == word

    def test_command_input(self):
        stdin = "baloogs"
        c = Command(["cat", "-"], stdin=stdin)

        res = c.run()
        assert res.stdout.strip() == stdin

    def test_assert_run(self):
        c = Command(["false"])
        self.assertRaises(hark.exceptions.CommandFailed, c.assertRun)
        c = Command(["true"])
        assert c.assertRun().exit_status == 0


class TestTerminalCommand(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_terminal_command(self, mockPopen):
        mockInstance = mockPopen.return_value
        mockInstance.wait.return_value = 1

        cmd = TerminalCommand(['ls', '/tmp'])
        ret = cmd.run()

        assert ret == 1
        assert mockPopen.called_with(cmd, sys.stdin, sys.stdout, sys.stderr)
