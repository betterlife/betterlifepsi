# encoding=utf-8
from psi.app.utils.security_util import is_super_admin, exclude_super_admin_roles
from psi.app.views.components import DisabledBooleanField, ReadonlyStringField
from flask_babelex import lazy_gettext

from psi.app.views.base import ModelViewWithAccess, CycleReferenceValidator


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
        if is_created: # All models created from UI is not system role.
            model.is_system = False
        CycleReferenceValidator.validate(form, model, object_type='Role', parent='parent',
                                         children='sub_roles', is_created=is_created)

    column_list = ('id', 'name', 'description',)

    column_searchable_list = ('name', 'description', 'parent.name', 'parent.description')

    form_extra_fields = {
        'shadow_is_system': DisabledBooleanField(label=lazy_gettext('System Role')),
        'shadow_name': ReadonlyStringField(label=lazy_gettext('Name'))
    }

    form_args = dict(
        name=dict(label=lazy_gettext('Name'),
                  description=lazy_gettext('Name will not be editable after the role been created.')),
    )

    column_labels = dict(
        id=lazy_gettext('id'),
        description=lazy_gettext('Description'),
        users=lazy_gettext('User'),
        sub_roles=lazy_gettext('Sub Roles'),
        parent=lazy_gettext('Parent Role'),
        is_system = lazy_gettext('System Role')
    )

    form_columns = ('parent', 'name', 'shadow_name','description', 'shadow_is_system', 'sub_roles', 'users')

    form_create_rules = ('parent', 'name', 'description', 'shadow_is_system', 'sub_roles', 'users')

    form_edit_rules = ('parent', 'shadow_name', 'description', 'shadow_is_system', 'sub_roles', 'users')

    column_editable_list = ('description',)

    column_sortable_list = ('id', 'name', 'description')

    column_details_list = ('id', 'name', 'description', 'is_system', 'parent', 'sub_roles', 'users')
