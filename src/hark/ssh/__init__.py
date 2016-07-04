import os

from hark.lib.command import TerminalCommand
import hark.lib.platform


def hark_ssh_keys():
    "Return a tuple of (private_key_path, public_key_path)"
    keydir = os.path.join(os.path.dirname(__file__), 'keys')
    return (
        os.path.join(keydir, 'hark'),
        os.path.join(keydir, 'hark.pub'),
    )


class InterativeSSHCommand(TerminalCommand):
    "SSH interactively into a machine."

    def __init__(self, port, user='hark'):
        if hark.lib.platform.isWindows():
            raise hark.exceptions.NotImplemented("SSH on windows")

        private_key_path, _ = hark_ssh_keys()

        cmd = (
            'ssh',
            # the port - probably mapping to host from guest
            '-p', str(port),
            # disable host key check - useless here
            '-o', 'StrictHostKeyChecking=no',
            # identity file: SSH private key
            '-i', private_key_path,
            # user and host
            '%s@localhost' % user,
        )

        TerminalCommand.__init__(self, *cmd)
