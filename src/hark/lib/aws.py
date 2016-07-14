

class S3Bucket(object):
    def __init__(
            self, s3_region, s3_bucket,
            aws_access_key_id=None, aws_secret_access_key=None):

        import boto3.session

        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=s3_region)

        self.s3 = session.client('s3')
        self.bucket = s3_bucket

    def list(self):
        params = {'Bucket': self.bucket}
        resp = self.s3.list_objects_v2(**params)
        return [o['Key'] for o in resp['Contents']]

    def signed_url(self, key):
        "Get a signed URL to GET an object"
        params = {'Bucket': self.bucket, 'Key': key}
        url = self.s3.generate_presigned_url(
                'get_object', Params=params)
        return url
