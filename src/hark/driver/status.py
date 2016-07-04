class status(object):

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

STOPPED = status('stopped')
RUNNING = status('running')
ABORTED = status('aborted')
PAUSED = status('paused')
