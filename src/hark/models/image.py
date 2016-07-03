import re

import hark.exceptions
import hark.models


_file_suffixes = {
        'virtualbox': 'vmdk',
}


class Image(hark.models.BaseModel):
    """
    A base image for running Hark machines.
    """

    fields = ['driver', 'guest', 'version']
    required = ['driver', 'guest', 'version']

    def file_suffix(self) -> str:
        return _file_suffixes[self['driver']]

    def file_path(self) -> str:
        return '%s_%s_v%d.%s' % (
            self['driver'], self['guest'],
            self['version'], self.file_suffix())

    _filePathMatch = r'^(\w+)_(.*)_v(\d+)\..*$'

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
