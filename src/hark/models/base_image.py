import re

import hark.exceptions
import hark.models


class BaseImage(hark.models.BaseModel):
    """
    A base image for building hark images.

    A base image is just for a particular guest, not a driver. When images are
    built and vendored for hark by the hark_builder tool, they become specified
    to both a guest and a driver.
    """

    fields = ['guest', 'version']
    required = ['guest', 'version']

    def file_suffix(self):
        return 'iso'

    def s3_path(self):
        return '%s/v%s.%s' % (
            self['guest'], self['version'], self.file_suffix())

    _s3PathMatch = r'^machine_images/base/(.*)/v(\d+)\.iso$'

    @classmethod
    def from_s3_path(cls, path):
        matches = re.findall(cls._s3PathMatch, path)
        if len(matches) != 1 or len(matches[0]) != 2:
            raise hark.exceptions.InvalidImagePath(
                '"%s" does not match "%s"' % (path, cls._s3PathMatch))
        guest, version = matches[0]
        return cls(
            guest=guest,
            version=int(version))
