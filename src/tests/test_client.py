import os
import tempfile
from unittest import TestCase
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock


import hark.client
import hark.dal
import hark.exceptions

from hark.models.image import Image
from hark.models.machine import Machine


class TestLocalClient(TestCase):
    """
    Basic tests of LocalClient with a mocked-out DAL.
    """

    @patch('hark.context.Context._initialize')
    @patch('hark.dal.DAL._connect')
    @patch('hark.context.imagecache.ImageCache._initialize')
    def setUp(self, mockInit, mockConnect, mockCacheInit):
        self.ctx = hark.context.Context('balooga')
        assert mockInit.called
        assert mockConnect.called
        assert mockCacheInit.called

    def testMachines(self):
        m = Machine(
                machine_id='1', name='foo',
                driver='yes', guest='no', memory_mb=512)

        mockRead = MagicMock(return_value=[m])
        self.ctx.dal.read = mockRead

        client = hark.client.LocalClient(self.ctx)

        machines = client.machines()

        assert isinstance(machines, list)
        assert len(machines) == 1
        assert machines[0] == m
        mockRead.assert_called_with(Machine)

    def testSaveMachine(self):
        m = Machine.new(name='foo', driver='yes', guest='no', memory_mb=512)

        mockSave = MagicMock(return_value=None)
        self.ctx.dal.create = mockSave

        client = hark.client.LocalClient(self.ctx)

        client.createMachine(m)

        mockSave.assert_called_with(m)

    def testGetMachine(self):
        m = Machine.new(name='foo', driver='yes', guest='no', memory_mb=512)
        client = hark.client.LocalClient(self.ctx)

        mockRead = MagicMock(return_value=[])
        self.ctx.dal.read = mockRead
        self.assertRaises(
            hark.exceptions.MachineNotFound,
            client.getMachine, m['name'])

        mockRead = MagicMock(return_value=[m])
        self.ctx.dal.read = mockRead
        assert client.getMachine(m['name']) == m

    def testLog(self):
        tf = tempfile.mktemp()
        try:
            msg = "ajlssljskl"
            with open(tf, 'w') as f:
                f.write(msg)

            self.ctx.log_file = MagicMock(return_value=tf)
            client = hark.client.LocalClient(self.ctx)

            logs = client.log()
            assert logs == msg
        finally:
            os.remove(tf)


class TestImagestoreClient(TestCase):

    def test_full_url(self):
        client = hark.client.ImagestoreClient('example.com')

        url = client._full_url('images')
        assert url == 'example.com/images'

    @patch('hark.client.ImagestoreClient._get')
    def test_images(self, mockGet):
        client = hark.client.ImagestoreClient('example.com')

        js = [
            {'driver': 'virtualbox', 'guest': 'Debian-7', 'version': 1},
            {'driver': 'virtualbox', 'guest': 'Debian-8', 'version': 1},
        ]
        expect = [Image(**j) for j in js]
        mockGet.return_value = js

        assert client.images() == expect

    @patch('hark.client.ImagestoreClient._get')
    def test_image_url(self, mockGet):
        client = hark.client.ImagestoreClient('example.com')
        url = 'http://blah.com'
        mockGet.return_value = {
            'url': url
        }
        im = Image(driver='virtualbox', guest='Debian-8', version='1')
        assert client.image_url(im) == url
        expectUrlCall = '/image/Debian-8/virtualbox/1'
        mockGet.assert_called_with(expectUrlCall)

    @patch('requests.session')
    def test_get(self, mockSession):
        client = hark.client.ImagestoreClient('example.com')
        expect = {'a': 'b'}

        session = mockSession.return_value
        mockResponse = session.get.return_value
        mockJson = mockResponse.json
        mockJson.return_value = expect

        res = client._get('images')

        assert res == expect
