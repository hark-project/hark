import os
import os.path

import hark.dal
import hark.log


class Context(object):
    def __init__(self, path):
        from hark.context.imagecache import ImageCache

        self.path = path

        self._initialize(path)

        dbpath = os.path.join(path, "hark.db")
        self.dal = hark.dal.DAL(dbpath)

        imagedir = os.path.join(path, 'images')
        self._image_cache = ImageCache(imagedir)

    def log_file(self):
        return os.path.join(self.path, 'hark.log')

    @classmethod
    def home(cls):
        home = os.path.expanduser("~")
        path = os.path.join(home, ".hark")
        return cls(path)

    def image_cache(self):
        return self._image_cache

    def _initialize(self, path):
        if not os.path.exists(path):
            hark.log.info("Creating hark base dir: %s", self.path)
            os.mkdir(path)
