import os
import os.path
import shutil
import tempfile
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from hark.context import Context
from hark.context.imagecache import ImageCache
from hark.models.image import Image


class TestContext(unittest.TestCase):
    def test_context(self):
        d = tempfile.mkdtemp()
        shutil.rmtree(d)
        Context(d)
        assert (os.path.exists(d)) is True
        dbpath = os.path.join(d, "hark.db")
        assert (os.path.exists(dbpath))
        shutil.rmtree(d)

    def test_context_home(self):
        ctx = Context.home()
        home = os.path.expanduser('~')
        assert ctx.path == os.path.join(home, '.hark')

    def test_context_log_file(self):
        d = tempfile.mkdtemp()
        try:
            ctx = Context(d)
            assert ctx.log_file() == os.path.join(d, 'hark.log')
        finally:
            shutil.rmtree(d)

    def test_image_cache(self):
        d = tempfile.mkdtemp()
        try:
            ctx = Context(d)
            ic = ctx.image_cache()
            assert isinstance(ic, ImageCache)
        finally:
            shutil.rmtree(d)


class TestImageCache(unittest.TestCase):
    def setUp(self):
        d = tempfile.mkdtemp()
        os.rmdir(d)
        self.tempdir = d

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_images(self):
        ic = ImageCache(self.tempdir)

        assert len(ic.images()) == 0

        # Create some fake images
        p = [
            'virtualbox_debian-8_v1.iso',
            'virtualbox_debian-7_v1.iso',
        ]
        for f in p:
            with open(os.path.join(self.tempdir, f), 'w') as f:
                    pass

        assert len(ic.images()) == 2

    def test_full_image_path(self):
        ic = ImageCache(self.tempdir)
        im = Image(driver='virtualbox', guest='debian-8', version=1)
        assert ic.full_image_path(im) == os.path.join(
            self.tempdir, im.file_path())

    @patch('shutil.copy')
    def test_save_from_file(self, mockCopy):
        ic = ImageCache(self.tempdir)
        im = Image(driver='virtualbox', guest='debian-8', version=1)
        tf = tempfile.mktemp()

        ic.saveFromFile(im, tf)

        mockCopy.assert_called_with(tf, ic.full_image_path(im))
