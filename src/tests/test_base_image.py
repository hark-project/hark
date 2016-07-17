import unittest

from hark.exceptions import InvalidImagePath
from hark.models.base_image import BaseImage


class TestImage(unittest.TestCase):

    def test_s3_path(self):
        img = BaseImage(guest='Debian-8', version=1)
        expect = 'Debian-8/v1.iso'
        assert img.s3_path() == expect

    def test_from_s3_path(self):
        path = 'machine_images/base/Debian-8/v1.iso'
        expect = BaseImage(guest='Debian-8', version=1)
        assert BaseImage.from_s3_path(path) == expect

        path = 'machine_images/base/Debian-8/1.iso'
        self.assertRaises(InvalidImagePath, BaseImage.from_s3_path, path)
