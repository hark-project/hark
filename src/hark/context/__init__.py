import os
import os.path

from hark.context.imagecache import ImageCache
import hark.dal
import hark.log


class Context(object):
    def __init__(self, path):
        self.path = path

        if not self._isInitialized():
            self._initialize(path)

        dbpath = os.path.join(path, "hark.db")
        self.dal = hark.dal.DAL(dbpath)

        imagedir = os.path.join(path, 'images')
        self.image_cache = ImageCache(imagedir)

    def log_file(self):
        return os.path.join(self.path, 'hark.log')

    @classmethod
    def home(cls):
        home = os.path.expanduser("~")
        path = os.path.join(home, ".hark")
        return cls(path)

    def _isInitialized(self):
        return os.path.exists(self.path)

    def _initialize(self, path):
        hark.log.info("Creating hark base dir: %s", self.path)
        os.mkdir(path)
