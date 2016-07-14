from unittest import TestCase
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock


from hark.lib.server import HTTPServer


class TestServer(TestCase):

    @patch('gunicorn.app.base.BaseApplication.run')
    def test_server_run(self, mockUnicornRun):
        app = MagicMock()

        s = HTTPServer(app, 9091, 1)
        s.run()

        mockUnicornRun.assert_has_calls(())

        assert s.gunicorn.options == {
            'bind': '127.0.0.1:9091',
            'workers': 1
        }
        assert s.gunicorn.load() == app
