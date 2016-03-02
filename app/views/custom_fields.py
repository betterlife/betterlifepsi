# coding=utf-8
from wtforms import StringField
from wtforms import widgets, fields


class DisabledStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(DisabledStringField, self).__call__(**kwargs)


class ReadonlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['readonly'] = 'readonly'
        return super(ReadonlyStringField, self).__call__(**kwargs)


''' Define a wtforms widget and field.
    WTForms documentation on custom widgets:
    http://wtforms.readthedocs.org/en/latest/widgets.html#custom-widgets
'''


class CKTextAreaWidget(widgets.TextArea):
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
