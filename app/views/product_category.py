# coding=utf-8
from flask.ext.babelex import lazy_gettext
from app.views import ModelViewWithAccess
from app.models import ProductCategory
from app.utils import form_util


class ProductCategoryAdmin(ModelViewWithAccess):
    column_sortable_list = ('id', 'code', 'name')
    column_searchable_list = ('code', 'name', 'parent_category.code', 'parent_category.name')
    column_filters = ('code', 'name', 'parent_category.code', 'parent_category.name')
    column_editable_list = ['code', 'name']

    column_details_list = ['id', 'name', 'code', 'parent_category', 'sub_categories', 'products']

    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'parent_category': lazy_gettext('Parent category'),
        'sub_categories': lazy_gettext('Sub Categories'),
        'products': lazy_gettext('Products'),
        'parent_category.code': lazy_gettext('Parent Category Code'),
        'parent_category.name': lazy_gettext('Parent Category Name'),
    }
    form_excluded_columns = ('sub_categories', 'products', 'organization')
    column_exclude_list = form_excluded_columns
    column_list = ('code', 'name', 'parent_category')

    def create_form(self, obj=None):
        form = super(ModelViewWithAccess, self).create_form(obj)
        form_util.filter_by_organization(form.parent_category, ProductCategory)
        return form

    def edit_form(self, obj=None):
        form = super(ModelViewWithAccess, self).edit_form(obj)
        form_util.filter_by_organization(form.parent_category, ProductCategory)
        return form
