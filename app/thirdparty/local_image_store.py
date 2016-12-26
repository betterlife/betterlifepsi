import os

import errno

from flask import current_app as app


class LocalImageStore(object):
    """
    A local image store service
    Images will be saved on static/uploaded folder
    """
    def __init__(self, app):
        pass

    @staticmethod
    def save(image_file, public_id):
        file_sep = '.'
        if (file_sep in image_file.filename
            and image_file.filename.rsplit(file_sep, 1)[1].lower() in app.config['IMAGE_ALLOWED_EXTENSIONS']):
            extension = image_file.filename.rsplit(file_sep, 1)[1].lower()
            filename = "{0}.{1}".format(public_id, extension)
            file_path_all = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path_all)
            result = {'url': "/static/uploaded/" + filename}
        else:
            result = {}
        return result

    @staticmethod
    def remove(path):
        """
           Remove a file from operation system and omit the error if it's not existing.
           :param filename: name of the file
           :return: None
           """
        try:
            os.remove(path)
        except OSError as e:
            # errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT:
                # re-raise exception if a different error occurred
                raise