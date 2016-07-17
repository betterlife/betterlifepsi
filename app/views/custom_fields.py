# coding=utf-8
from flask import url_for
from wtforms import StringField
from wtforms import widgets, fields
from wtforms.widgets import HTMLString


class DisabledStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(DisabledStringField, self).__call__(**kwargs)


class ReadonlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['readonly'] = 'readonly'
        return super(ReadonlyStringField, self).__call__(**kwargs)


class CKTextAreaWidget(widgets.TextArea):
    """
    Define a wtforms widget and field.
    WTForms documentation on custom widgets:
    http://wtforms.readthedocs.org/en/latest/widgets.html#custom-widgets
    """

    def __call__(self, field, **kwargs):
        # add WYSIWYG class to existing classes
        existing_classes = kwargs.pop('class', '') or kwargs.pop('class_', '')
        if (existing_classes is not None) and (len(existing_classes) == 0):
            clazz = "ckeditor"
        else:
            clazz = u'{0!s} {1!s}'.format(existing_classes, "ckeditor")
        kwargs['class'] = clazz
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(fields.TextAreaField):
    widget = CKTextAreaWidget()


class ImageInput(object):
    """
    Image upload controller, supports
    1. Multiple file upload one time
    2. Preview existing image files on server.
    3. Preview to be uploaded image files on the fly before uploading.
    Template file components/image_field.html is needed for this controller
    to work correctly.
    """
    def __call__(self, field, **kwargs):
        # Use field.data to get current data.
        from flask import render_template
        associated_images = []
        if field.data is not None and len(field.data) > 0:
            for p_i in field.data:
                associated_images.append(p_i)
        else:
            associated_images = []
        return render_template('components/image_input.html',
                               associated_images=associated_images)


class ImageField(StringField):
    widget = ImageInput()

    def __call__(self, **kwargs):
        return super(ImageField, self).__call__(**kwargs)

    def populate_obj(self, obj, name):
        from flask import request
        from app.service import Info
        from app.models import ProductImage
        from app.utils import file_util, db_util
        images_to_del = request.form.get('images-to-delete')
        if len(images_to_del) > 0:
            to_del_ids = images_to_del.split(',')
            for to_del_id in to_del_ids:
                db_util.delete_by_id(ProductImage, to_del_id, commit=False)
        files = request.files.getlist('images_placeholder')
        for f in files:
            if len(f.filename) > 0:
                product_image = ProductImage()
                product_image.product = obj
                image = file_util.save_image(product_image, f)
                Info.get_db().session.add(image)
                Info.get_db().session.add(product_image)


