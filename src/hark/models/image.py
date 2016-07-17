import re

import hark.exceptions
import hark.models


_file_suffixes = {
        'virtualbox': 'vmdk',
}


class Image(hark.models.BaseModel):
    """
    An  image for running Hark machines.
    """

    fields = ['driver', 'guest', 'version']
    required = ['driver', 'guest', 'version']

    def file_suffix(self):
        return _file_suffixes[self['driver']]

    def file_path(self):
        return '%s_%s_v%d.%s' % (
            self['driver'], self['guest'],
            self['version'], self.file_suffix())

    _filePathMatch = r'^(\w+)_(.*)_v(\d+)\..*$'

    def s3_path(self):
        return '%s/%s/v%d.%s' % (
            self['guest'], self['driver'],
            self['version'], self.file_suffix())

    @classmethod
    def from_file_path(cls, path):
        matches = re.findall(cls._filePathMatch, path)
        if len(matches) != 1 or len(matches[0]) != 3:
            raise hark.exceptions.InvalidImagePath(
                '"%s" does not match "%s"' % (path, cls._filePathMatch))
        driver, guest, version = matches[0]

        return cls(
            driver=driver,
            guest=guest,
            version=int(version))

    _s3PathMatch = r'^machine_images/built/(.*)/(.*)/v(\d+)\..*$'

    @classmethod
    def from_s3_path(cls, path):
        matches = re.findall(cls._s3PathMatch, path)
        if len(matches) != 1 or len(matches[0]) != 3:
            raise hark.exceptions.InvalidImagePath(
                '"%s" does not match "%s"' % (path, cls._s3PathMatch))
        guest, driver, version = matches[0]
        return cls(
            driver=driver,
            guest=guest,
            version=int(version))
