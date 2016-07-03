import unittest

import hark.exceptions
from hark.lib.command import which, Command, Result, run_all


class TestWhich(unittest.TestCase):
    def test_which(self):
        expect = ('/bin/true', '/usr/bin/true')

        path = which('true')
        assert path in expect

        path = which('fhdljhfdjdfkljsd')
        assert path is None


class TestCommand(unittest.TestCase):
    def test_command_result_true_false(self):
        for c, status in (("true", 0), ("false", 1)):
            command = Command(c)

            res = command.run()
            assert isinstance(res, Result)
            assert res.exit_status == status
            assert len(res.stdout) == 0
            assert len(res.stderr) == 0

    def test_command_output(self):
        word = "blaaaa"
        c = Command("echo", word)

        res = c.run()
        assert res.stdout.strip() == word

    def test_command_input(self):
        stdin = "baloogs"
        c = Command("cat", "-", stdin=stdin)

        res = c.run()
        assert res.stdout.strip() == stdin

    def test_run_all(self):
        c1 = Command("true")
        c2 = Command("false")

        results = run_all(c1, c2)

        assert len(results) == 2
        assert results[0].exit_status == 0
        assert results[1].exit_status == 1

    def test_assert_run(self):
        c = Command("false")
        self.assertRaises(hark.exceptions.CommandFailed, c.assertRun)
        c = Command("true")
        assert c.assertRun().exit_status == 0
