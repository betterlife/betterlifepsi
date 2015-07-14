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
        kwargs['class'] = u'%s %s' % (existing_classes, "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(fields.TextAreaField):
    widget = CKTextAreaWidget()