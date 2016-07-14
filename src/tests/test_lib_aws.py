from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import hark.lib.aws


class TestS3Bucket(TestCase):

    @patch('boto3.session.Session.client')
    def test_list(self, mockClient):
        mockS3 = mockClient.return_value
        mockList = mockS3.list_objects_v2
        ret = {
            'Contents': [
                {'Key': 'foo'},
                {'Key': 'foo/bar'},
                {'Key': 'foo/bar/bang'},
                {'Key': 'foo/baz/born'},
                {'Key': 'foo/baz/born/bista'},
            ]
        }
        mockList.return_value = ret

        bucket = hark.lib.aws.S3Bucket('mybucket', 'myregion', 'a', 'b')
        mockClient.assert_called_with('s3')

        expect = [o['Key'] for o in ret['Contents']]

        assert bucket.list() == expect
