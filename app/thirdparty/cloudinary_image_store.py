from cloudinary import uploader


class ImageStore(object):
    def __init__(self, app):
        pass

    @staticmethod
    def save(image_file, public_id):
        res = uploader.upload(
            image_file,
            public_id=public_id,
        )
        return res

    @staticmethod
    def remove(public_id):
        res = uploader.destroy(public_id)
        return res
