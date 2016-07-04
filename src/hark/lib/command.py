import asyncio
from asyncio.subprocess import PIPE as AIOPIPE
from subprocess import PIPE
import subprocess
import sys
from typing import List

import hark.exceptions
import hark.log

from . import platform


def which(cmd):
    "find the full path to a command; return None if not found"
    if platform.isWindows():
        raise hark.exceptions.NotImplemented("which() on windows")
    c = Command("which", cmd)
    res = c.run()
    if res.exit_status != 0:
        return None
    return res.stdout.strip()


class Result(object):
    """
    The result of a command.

    The bytes of stdout and stderr are assumed to be UTF-8 strings and are
    decoded as such.
    """
    def __init__(self, cmd, exit_status, stdout, stderr):
        self.cmd = cmd
        self.exit_status = exit_status
        self.stdout = stdout.decode('utf-8')
        self.stderr = stderr.decode('utf-8')


class Command(object):
    def __init__(self, *cmd: List[str], stdin: str="") -> None:
        self.cmd = cmd
        self.stdin = stdin

    def run(self) -> Result:
        "Run this command and return a Result object"
        hark.log.debug("Running command: %s", self.cmd)
        proc = subprocess.Popen(
            self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        out, err = proc.communicate(self.stdin.encode('utf-8'))
        status = proc.wait()

        return Result(self.cmd, status, out, err)

    def assertRun(self):
        "Run a command and throw an exception if exit_status is not 0"
        res = self.run()
        if res.exit_status != 0:
            raise hark.exceptions.CommandFailed(self, res)
        return res

    @asyncio.coroutine
    def _run(self):
        """
        Run a command with asyncio, returning a Future.

        Useful to compose multiple subprocesses running concurrently.
        """
        proc = yield from asyncio.create_subprocess_exec(
            *self.cmd, stdin=AIOPIPE, stdout=AIOPIPE, stderr=AIOPIPE)

        out, err = yield from proc.communicate(self.stdin.encode('utf-8'))
        status = yield from proc.wait()

        return Result(self.cmd, status, out, err)


class TerminalCommand(object):
    "A command that will be attached to the terminal"
    def __init__(
            self, *cmd: List[str],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr):
        self.cmd = cmd
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def run(self) -> None:
        "Run this command interactively. Return its exit status."
        hark.log.debug("Running command attached to terminal: %s", self.cmd)
        proc = subprocess.Popen(
            self.cmd,
            stdin=self.stdin, stdout=self.stdout, stderr=self.stderr)
        return proc.wait()


def run_all(*commands: List[Command]) -> List[Result]:
    "Run a set of commands concurrently with asyncio"
    pending = [c._run() for c in commands]
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyncio.gather(*pending))
    return res
