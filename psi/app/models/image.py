# coding=utf-8

from psi.app.service import Info
from sqlalchemy import event

db = Info.get_db()


class Image(db.Model):
    """
    Meta for images uploaded to the system
    """
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    alt = db.Column(db.Unicode(256))
    path = db.Column(db.String(128), nullable=False)
    public_id = db.Column(db.String(128), nullable=True)


@event.listens_for(Image, 'after_delete')
def _handle_image_delete(mapper, conn, target):
    """
    Delete the local or remote image from 3rd service when delete the image.
    if path is not empty, assume local storage, delete using after_delete
    listener, if public_id is not null, assume using cloud service, delete
    using public_id.
    :param mapper:
    :param conn:
    :param target: image object to be deleted
    :return:
    """
    # TODO.xqliu The delete of image is not working for local image store
    Info.get_image_store_service().remove(target.path, target.public_id)
