import os

from hark.lib.command import Command, TerminalCommand
import hark.lib.platform


def hark_ssh_keys():
    "Return a tuple of (private_key_path, public_key_path)"
    keydir = os.path.join(os.path.dirname(__file__), 'keys')
    keys = ('hark', 'hark.pub')
    return (os.path.join(keydir, k) for k in keys)


def check_ssh(port, user='hark'):
    "Return whether SSH is available"
    cmd = RemoteShellCommand("true", port)
    ret = cmd.run()
    return ret.exit_status == 0


def _ssh_command_args(port, user):
        private_key_path, _ = hark_ssh_keys()

        cmd = [
            'ssh',
            # the port - probably mapping to host from guest
            '-p', str(port),
            # disable host key check - useless here
            '-o', 'StrictHostKeyChecking=no',
            # identity file: SSH private key
            '-i', private_key_path,
            # user and host
            '%s@localhost' % user,
        ]

        return cmd


class RemoteShellCommand(Command):
    "Run a shell script remotely on a machine over SSH."

    def __init__(self, cmd, port, user='hark'):
        sshCmd = _ssh_command_args(port, user)
        Command.__init__(
            self, sshCmd,
            stdin=cmd)


class InterativeSSHCommand(TerminalCommand):
    "SSH interactively into a machine."

    def __init__(self, port, user='hark'):
        if hark.lib.platform.isWindows():
            raise hark.exceptions.NotImplemented("SSH on windows")

        cmd = _ssh_command_args(port, user)
        TerminalCommand.__init__(self, cmd)


_sshConfigTmpl = """Host {name}
    HostName 127.0.0.1
    User hark
    Port {port}
    UserKnownHostsFile /dev/null
    StrictHostKeyChecking no
    PasswordAuthentication no
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    LogLevel FATAL
    ForwardAgent {forward_agent}
"""


class SSHConfig(object):
    """
    SSHConfig, given a machine and mapping model, can generate the appropriate
    OpenSSH config for this machine.
    """
    def __init__(self, machine, mapping, forward_agent=False):
        self.machine = machine
        self.mapping = mapping
        self.forward_agent = forward_agent

    def __str__(self):
        private_key_path, _ = hark_ssh_keys()
        fw = 'yes' if self.forward_agent else 'no'

        return _sshConfigTmpl.format(
            name=self.machine['name'],
            port=self.mapping['host_port'],
            private_key_path=private_key_path,
            forward_agent=fw,
        )
