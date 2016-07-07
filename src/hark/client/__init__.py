from typing import List

import requests
from requests.models import Response

import hark.exceptions
import hark.log as log
from hark.models.image import Image
from hark.models.machine import Machine
from hark.models.port_mapping import PortMapping
from hark.imagestore import URLS as IMAGESTORE_URLS
import hark.util.download


class LocalClient(object):
    def __init__(self, context):
        self._context = context

    def dal(self):
        return self._context.dal

    def log(self) -> str:
        with open(self._context.log_file(), 'r') as f:
            return f.read()

    def machines(self) -> List[Machine]:
        "Get all machines"
        return self.dal().read(Machine)

    def createMachine(self, machine: Machine) -> None:
        log.debug('Saving machine: %s', machine.json())
        self.dal().create(machine)

    def getMachine(self, name) -> Machine:
        "Get a machine by name."
        m = self.dal().read(Machine, constraints={"name": name})
        if len(m) == 0:
            raise hark.exceptions.MachineNotFound
        return m[0]

    def portMappings(self, name=None, machine_id=None) -> List[PortMapping]:
        "Get all port mappings"
        constraints = {}
        if name is not None:
            constraints['name'] = name
        if machine_id is not None:
            constraints['machine_id'] = machine_id

        return self.dal().read(PortMapping, constraints=constraints)

    def createPortMapping(self, mapping: PortMapping) -> None:
        log.debug('Saving port mapping: %s', mapping)
        self.dal().create(mapping)

    def images(self) -> List[Image]:
        "Return the list of locally cached images"
        return self._context.image_cache().images()

    def imagePath(self, image: Image):
        "Get the full file path to an image"
        return self._context.image_cache().full_image_path(image)

    def saveImageFromFile(self, image: Image, source: str):
        self._context.image_cache().saveFromFile(image, source)

    def saveImageFromUrl(self, image: Image, url: str):
        resp = requests.get(url, stream=True)
        f = open(self.imagePath(image), 'wb')

        try:
            hark.util.download.responseToFile(
                'Downloading:', resp, f)
        finally:
            resp.close()
            f.close()


class ImagestoreClient(object):
    def __init__(self, url: str) -> None:
        self.session = requests.session()
        self.base_url = url
        self.session.headers['Accept'] = 'application/json'

    def _full_url(self, url: str) -> str:
        return "%s/%s" % (self.base_url, url)

    def _get(self, url: str) -> Response:
        response = self.session.get(self._full_url(url))
        response.raise_for_status()
        return response.json()

    def images(self) -> List[Image]:
        js = self._get(IMAGESTORE_URLS['images'])
        return [Image(**o) for o in js]

    def image_url(self, image: Image) -> str:
        url = IMAGESTORE_URLS['image'].format(**image)
        js = self._get(url)
        return js['url']
