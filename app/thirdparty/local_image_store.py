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
            result = {'url': "/static/uploaded/" + filename, 'filename': filename}
        else:
            result = {}
        return result

    @staticmethod
    def remove(path, public_id):
        """
           Remove a file from operation system and omit the error if it's not existing.
           :param public_id: public_id of the file(used for public storage service to save it's id)
           :param path: path of the file when render it in UI
           :return: None
           """
        try:
            file_absolute_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(path))
            os.remove(file_absolute_path)
        except OSError as e:
            # errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT:
                # re-raise exception if a different error occurred
                raise