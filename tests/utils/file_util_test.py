import os
import unittest

import io

from werkzeug.datastructures import FileStorage

from app.utils.file_util import save_image
from tests import fixture
from tests.base_test_case import BaseTestCase


class TestFileUtil(BaseTestCase):

    def setUp(self):
        super(TestFileUtil, self).setUp()
        test_image_file_path = os.path.join(os.path.dirname(__file__), '../resources/image.png')
        self.image_file = open(test_image_file_path)

    def tearDown(self):
        super(TestFileUtil, self).tearDown()
        self.image_file.close()


    def testSaveImage(self):
        from app.models.product import ProductImage
        owner = ProductImage()
        data = self.image_file.read()
        stream = io.BytesIO(data)
        image = FileStorage(content_type='image/png', name='image_placeholder',
                            filename=u'/etc/init.d/functions.png', content_length=0, stream=stream)
        image = save_image(owner, image)
        self.assertIsNotNone(owner.image)
        self.assertIsNotNone(image)
        self.assertIsNotNone(image.path)
        self.assertIsNotNone(image.public_id)
        self.assertIn(image.public_id, image.path)


