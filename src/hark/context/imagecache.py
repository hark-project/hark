import os
import shutil

import hark.log as log
from hark.models.image import Image


class ImageCache(object):
    "A local cache of image files."

    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            log.info("Creating hark image dir: %s", path)
            self._initialize()

    def _initialize(self):
        os.mkdir(self.path)

    def images(self):
        "The list of cached images, sorted by ascending version"
        os.listdir(self.path)
        im = []
        for f in os.listdir(self.path):
            im.append(Image.from_file_path(f))
        return list(sorted(
            im,
            key=lambda i: i['version']))

    def full_image_path(self, image):
        return os.path.join(self.path, image.file_path())

    def saveFromFile(self, image, source):
        dest = self.full_image_path(image)
        log.info(
            "Copying local file %s to destination image %s",
            source, dest)
        shutil.copy(source, dest)
