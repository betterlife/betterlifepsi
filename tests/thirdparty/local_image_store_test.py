from __future__ import print_function

import os
import unittest
import uuid
import io
from werkzeug.datastructures import FileStorage

from app.thirdparty.local_image_store import LocalImageStore
from tests import fixture


class TestLocalImageStore(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        test_image_file_path = os.path.join(os.path.dirname(__file__), 'image.png')
        self.image_file = open(test_image_file_path)

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()
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
        uploaded_file = open(file_absolute_path)
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







