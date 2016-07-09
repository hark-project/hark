from unittest import TestCase


class TestHarkCLI(TestCase):

    def test_import_hark_cli(self):
        from hark.cli.hark import hark_main

        assert callable(hark_main)
