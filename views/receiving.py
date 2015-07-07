# coding=utf-8
from flask.ext.admin.model import InlineFormAdmin
from models import ReceivingLine, Receiving
from views import ModelViewWithAccess

class ReceivingLineInlineAdmin(InlineFormAdmin):
    pass

class ReceivingAdmin(ModelViewWithAccess):
    inline_models = (ReceivingLineInlineAdmin(ReceivingLine),)

    form_args = dict(
        status=dict(query_factory=Receiving.status_filter),
    )
