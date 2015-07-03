# coding=utf-8
from wtforms import StringField

class ReadOnlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(ReadOnlyStringField, self).__call__(**kwargs)