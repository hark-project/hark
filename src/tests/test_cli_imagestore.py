from unittest import TestCase


class TestHarkImagestoreCLI(TestCase):

    def test_import_hark_imagestore_cli(self):
        from hark.cli.hark_imagestore import hark_imagestore

        assert callable(hark_imagestore)
