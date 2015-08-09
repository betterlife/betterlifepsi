# coding=utf-8
from flask.ext.babelex import lazy_gettext
from views import ModelViewWithAccess

class ProductCategoryAdmin(ModelViewWithAccess):
    column_exclude_list = ['sub_categories', 'products']

    column_sortable_list = ('id', 'code', 'name')
    column_searchable_list = ('code', 'name')
    # column_filters = ('code','name')
    column_editable_list = ['code', 'name']
    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'parent_category': lazy_gettext('Parent category'),
    }
    form_excluded_columns = ('sub_categories', 'products')
