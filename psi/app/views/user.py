# coding=utf-8
from functools import partial

from psi.app.utils.security_util import is_super_admin
from flask_login import current_user
from flask_babelex import lazy_gettext
from flask_security.utils import encrypt_password
from sqlalchemy import func
from wtforms import PasswordField

from psi.app.views.base import ModelViewWithAccess


# Customized User model for SQL-Admin
class UserAdmin(ModelViewWithAccess):

    from psi.app.views.formatter import organization_formatter
    from psi.app.models.user import User

    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    column_list = ('id', 'login', 'display', 'email', 'organization', 'active',)

    """
    Disable delete of user(use de-active instead)
    """
    can_delete = False

    # Not working by now
    # column_editable_list = ('display', 'email', 'active')

    column_details_list = ('id', 'login', 'display', 'email', 'active', 'roles', 'locale', 'timezone')

    form_columns = ('login', 'display', 'email', 'locale', 'timezone', 'active', 'organization', 'roles',)

    column_filters = ('active',)

    column_searchable_list = ('login', 'display', 'email',)

    column_labels = dict(
        id=lazy_gettext('id'),
        login=lazy_gettext('Login Name'),
        display=lazy_gettext('Display'),
        email=lazy_gettext('Email'),
        active=lazy_gettext('Active'),
        roles=lazy_gettext('Role'),
        organization=lazy_gettext('Organization'),
    )

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    column_formatters = {
        'organization': organization_formatter
    }

    form_args = dict(
        active=dict(description=lazy_gettext('Un-check this checkbox to disable a user from login to the system')),
        organization=dict(description=lazy_gettext('You can only create/modify user belongs to your organization and sub-organization')),
        locale=dict(label=lazy_gettext('Language'), query_factory=User.locale_filter),
        timezone=dict(label=lazy_gettext('Timezone'), query_factory=User.timezone_filter),
    )

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        # autocomplete:new-password is to disable chrome to autofill password
        # Reference: http://stackoverflow.com/questions/15738259/disabling-chrome-autofill
        form_class.password2 = PasswordField(label=lazy_gettext('New Password'),
                                             render_kw={"autocomplete": "new-password"},
                                             description=lazy_gettext('Left blank if you don\'t want to change it, '
                                                                      'input the new password to change it'))
        return form_class

    def create_form(self, obj=None):
        from psi.app.models import Organization

        form = super(UserAdmin, self).create_form(obj)
        form.organization.query_factory = partial(Organization.children_self_filter, current_user.organization)
        return form

    def edit_form(self, obj=None):
        from psi.app.models import Organization

        form = super(UserAdmin, self).edit_form(obj)
        form.organization.query_factory = partial(Organization.children_self_filter, current_user.organization)
        return form

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        if not is_super_admin():
            super(UserAdmin, self).on_model_change(form, model, is_created)
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = encrypt_password(model.password2)

    def get_query(self):
        """
        For cross organization super admin, return all the users
        For organization specify admin, only return users of it's own's organization
        :return:
        """
        return self.session.query(self.model) if is_super_admin() else super(UserAdmin, self).get_query()

    def get_count_query(self):
        """
        For cross organization super admin, return all the users
        For organization specify admin, only return users of it's own's organization
        :return:
        """
        return self.session.query(func.count('*')).select_from(self.model) \
            if is_super_admin() \
            else super(UserAdmin, self).get_count_query()
