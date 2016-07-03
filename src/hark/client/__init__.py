from typing import List

import hark.exceptions
import hark.log as log
from hark.models.image import Image
from hark.models.machine import Machine


class LocalClient(object):
    def __init__(self, context):
        self._context = context

    def dal(self):
        return self._context.dal

    def log(self) -> str:
        with open(self._context.log_file(), 'r') as f:
            return f.read()

    def machines(self) -> List[Machine]:
        return self.dal().read(Machine)

    def createMachine(self, machine: Machine):
        log.debug('Saving machine: %s', machine.json())
        self.dal().create(machine)

    def getMachine(self, name) -> Machine:
        "Get a machine by name."
        m = self.dal().read(Machine, constraints={"name": name})
        if len(m) == 0:
            raise hark.exceptions.MachineNotFound
        elif len(m) > 1:
            # TODO(cera) - Name this exception.
            raise Exception("More than one machine found for name " + name)
        return m[0]

    def images(self) -> List[Image]:
        "Return the list of locally cached images"
        return self._context.image_cache.images()

    def imagePath(self, image: Image):
        "Get the full file path to an image"
        return self._context.image_cache.full_image_path(image)

    def saveImageFromFile(self, image: Image, source: str):
        self._context.image_cache.saveFromFile(image, source)
