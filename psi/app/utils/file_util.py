from psi.app.service import Info
import uuid


def save_image(owner, image_file):
    """
    Save image to an owner object
    :param service: The service to save the image,
                    use to isolate different storage service
    :param owner: Owner of this image object
    :param image_file: File storage object of the image
    :return: The image object created
    """
    from psi.app.models import Image
    service = Info.get_image_store_service()
    if owner.image is not None:
        existing_img_public_id = owner.image.path
        service.remove(existing_img_public_id)
    image = Image()
    owner.image = image
    public_id = str(uuid.uuid4())
    result = service.save(image_file, public_id=public_id)
    owner.image.path = result['url']
    owner.image.public_id = public_id
    return image
