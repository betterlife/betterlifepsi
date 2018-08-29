from __future__ import print_function

import os
import unittest
import uuid
import io
from werkzeug.datastructures import FileStorage

from psi.app.thirdparty.local_image_store import LocalImageStore
from tests.base_test_case import BaseTestCase


class TestLocalImageStore(BaseTestCase):
    def setUp(self):
        super(TestLocalImageStore, self).setUp()
        test_image_file_path = os.path.join(os.path.dirname(__file__), '../resources/image.png')
        self.image_file = open(test_image_file_path, 'rb')

    def tearDown(self):
        super(TestLocalImageStore, self).tearDown()
        self.image_file.close()

    def testLocalImageSaveAndRemove(self):
        public_id = str(uuid.uuid4())

        data = self.image_file.read()
        stream = io.BytesIO(data)
        image = FileStorage(content_type='image/png', filename=u'/etc/init.d/functions.png', name='image_placeholder',
                            content_length=0, stream=stream)
        result = LocalImageStore.save(image, public_id)
        self.assertIsNotNone(result)
        filename = public_id + ".png"
        self.assertEqual(result['url'], "/static/uploaded/" + filename)
        self.assertEqual(result['filename'], filename)
        file_absolute_path = os.path.join(self.app.config['UPLOAD_FOLDER'], result['filename'])
        uploaded_file = open(file_absolute_path, 'rb')
        uploaded_data = uploaded_file.read()
        self.assertEqual(data, uploaded_data)
        uploaded_file.close()
        LocalImageStore.remove(file_absolute_path, public_id)
        try:
            uploaded_file = open(file_absolute_path)
            uploaded_file.close()
        except IOError as e:
            pass
        else:
            self.fail("The file should be deleted!")







