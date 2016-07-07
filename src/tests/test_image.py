import unittest

from hark.exceptions import InvalidImagePath
from hark.models.image import Image


class TestImage(unittest.TestCase):

    def test_file_path(self):
        img = Image(driver='virtualbox', guest='Debian-8', version=1)
        expect = 'virtualbox_Debian-8_v1.vmdk'
        assert img.file_path() == expect

    def test_s3_path(self):
        img = Image(driver='virtualbox', guest='Debian-8', version=1)
        expect = 'Debian-8/virtualbox/v1.vmdk'
        assert img.s3_path() == expect

    def test_from_file_path(self):
        path = 'virtualbox_Debian-8_v1.vmdk'
        expect = Image(driver='virtualbox', guest='Debian-8', version=1)
        assert Image.from_file_path(path) == expect

        path = 'virtualbox-Debian-8_v1.vmdk'
        self.assertRaises(InvalidImagePath, Image.from_file_path, path)

    def test_from_s3_path(self):
        path = 'machine_images/built/Debian-8/virtualbox/v1.vmdk'
        expect = Image(driver='virtualbox', guest='Debian-8', version=1)
        assert Image.from_s3_path(path) == expect

        path = 'machine_images/built/Debian-8/virtualbox/1.vmdk'
        self.assertRaises(InvalidImagePath, Image.from_s3_path, path)
