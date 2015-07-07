# coding=utf-8
from wtforms import StringField

class DisabledStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(DisabledStringField, self).__call__(**kwargs)

class ReadonlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['readonly'] = 'readonly'
        return super(ReadonlyStringField, self).__call__(**kwargs)