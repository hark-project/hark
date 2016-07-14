import os
import os.path

import hark.dal
import hark.log


class Context(object):
    def __init__(self, path):
        from hark.context.imagecache import ImageCache

        self.path = path

        if not self._isInitialized():
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

    def _isInitialized(self):
        return os.path.exists(self.path)

    def _initialize(self, path):
        hark.log.info("Creating hark base dir: %s", self.path)
        os.mkdir(path)


class RemoteContext(object):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None):

        from hark.context.imagecache import S3ImageCache

        self._image_cache = S3ImageCache(
            aws_access_key_id, aws_secret_access_key)

    def image_cache(self):
        return self._image_cache
