# encoding=utf-8
from app.utils.security_util import is_super_admin, exclude_super_admin_roles
from app.views.base import ModelViewWithAccess, CycleReferenceValidator
from flask_babelex import lazy_gettext


class RoleAdmin(ModelViewWithAccess):
    def is_accessible(self):
        return is_super_admin()

    def get_query(self):
        if not is_super_admin():
            return exclude_super_admin_roles(self.model.name, super(RoleAdmin, self).get_query())
        return super(RoleAdmin, self).get_query()

    def get_count_query(self):
        if not is_super_admin():
            return exclude_super_admin_roles(self.model.name, super(RoleAdmin, self).get_count_query())
        return super(RoleAdmin, self).get_count_query()

    def on_model_change(self, form, model, is_created):
        """Check whether the parent role is same as child role"""
        super(RoleAdmin, self).on_model_change(form, model, is_created)
        CycleReferenceValidator.validate(form, model, object_type='Role', parent='parent',
                                         children='sub_roles', is_created=is_created)

    column_list = ('id', 'name', 'description',)

    column_searchable_list = ('name', 'description', 'parent.name', 'parent.description')

    column_labels = dict(
        id=lazy_gettext('id'),
        name=lazy_gettext('Name'),
        description=lazy_gettext('Description'),
        users=lazy_gettext('User'),
        sub_roles=lazy_gettext('Sub Roles'),
        parent=lazy_gettext('Parent Role')
    )
    column_editable_list = ('description',)

    column_sortable_list = ('id', 'name', 'description')

    column_details_list = ('id', 'name', 'description', 'parent', 'sub_roles', 'users')
