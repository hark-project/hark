import click
from io import BufferedWriter
from requests import Response


def responseToFile(msg: str, response: Response, f: BufferedWriter):
    """
    Download a response object to a value. Print a progress bar with click.

    Assumes that stream=True was passed to requests.
    """
    chunk_size = 1024
    length = int(response.headers['Content-Length'])
    with click.progressbar(length=length, label=msg) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
            bar.update(chunk_size)
        f.flush()
