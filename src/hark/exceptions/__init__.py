class NotImplemented(Exception):
    pass


class InvalidImagePath(Exception):
    pass


class ModelInvalidException(Exception):
    def __init__(self, instance, reason) -> None:
        self.model = instance
        name = instance.__class__.__name__
        msg = "%s invalid: %s" % (name, reason)
        Exception.__init__(self, msg)


class InvalidMachineException(Exception):
    pass


class InvalidQueryConstraint(Exception):
    pass


class DuplicateModelException(Exception):
    def __init__(self, instance):
        self.model = instance
        name = instance.__class__.__name__
        msg = "A %s with the same field values already exists" % name
        Exception.__init__(self, msg)


class UnknownGuestException(Exception):
    pass


class UnknownDriverException(Exception):
    pass


class CommandFailed(Exception):
    def __init__(self, command, result):
        self.command = command
        self.result = result
        msg = "Command '%s' had exit_status %d and stderr: '%s'" % (
            command.cmd, result.exit_status, result.stderr)
        Exception.__init__(self, msg)


class MachineNotFound(Exception):
    pass


class ImageNotFound(Exception):
    pass


class UnrecognisedMachineState(Exception):
    pass
