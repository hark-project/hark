import os
import shutil
from typing import List, Optional

import hark.lib.aws
import hark.log as log
from hark.models.image import Image

DEFAULT_S3_REGION = 'ap-southeast-2'
DEFAULT_S3_BUCKET = 'harkvm'
BUILT_IMAGE_PREFIX = 'machine_images/built'


class ImageCache(object):
    "A local cache of image files."

    def __init__(self, path) -> None:
        self.path = path
        if not os.path.exists(path):
            log.info("Creating hark image dir: %s", path)
            self._initialize()

    def _initialize(self) -> None:
        os.mkdir(self.path)

    def images(self) -> List[Image]:
        "The list of cached images, sorted by ascending version"
        os.listdir(self.path)
        im = []
        for f in os.listdir(self.path):
            im.append(Image.from_file_path(f))
        return list(sorted(
            im,
            key=lambda i: i['version']))

    def full_image_path(self, image: Image) -> str:
        return os.path.join(self.path, image.file_path())

    def saveFromFile(self, image: Image, source: str):
        dest = self.full_image_path(image)
        log.info(
            "Copying local file %s to destination image %s",
            source, dest)
        shutil.copy(source, dest)


class S3ImageCache(object):
    def __init__(
            self,
            aws_access_key_id: Optional[str]=None,
            aws_secret_access_key: Optional[str]=None) -> None:
        self.bucket = hark.lib.aws.S3Bucket(
            DEFAULT_S3_REGION, DEFAULT_S3_BUCKET,
            aws_access_key_id, aws_secret_access_key)

    def images(self) -> List[Image]:
        objects = self.bucket.list()
        objects = [
            o for o in objects
            if o.startswith('machine_images/built/')
            and len(o.split('/')) == 5
            and '.' in o
        ]
        im = []
        for obj in objects:
            image = Image.from_s3_path(obj)
            im.append(image)
        return im

    def full_image_path(self, image: Image) -> str:
        return self.bucket.signed_url(
            os.path.join(BUILT_IMAGE_PREFIX, image.s3_path())
        )
