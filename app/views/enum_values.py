# coding=utf-8
from flask.ext.babelex import lazy_gettext
from app.views import ModelViewWithAccess

class EnumValuesAdmin(ModelViewWithAccess):
    column_list = ('id', 'code', 'display', 'type')

    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']

    column_details_list = ['id', 'code', 'display', 'type', 'type_values']

    # column_filters = ('code', 'display',)
    column_labels = {
        'id': lazy_gettext('id'),
        'type': lazy_gettext('Type'),
        'code': lazy_gettext('Code'),
        'display': lazy_gettext('Display'),
        'type_values': lazy_gettext('Type Values'),
    }