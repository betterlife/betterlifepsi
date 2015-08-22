# coding=utf-8
from flask.ext.babelex import lazy_gettext
from app.views import ModelViewWithAccess
from wtforms import PasswordField
from werkzeug.security import generate_password_hash

# Customized User model for SQL-Admin
class UserAdmin(ModelViewWithAccess):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    column_list = ('id', 'login', 'display', 'email', 'active',)

    column_editable_list = ('display', 'email', 'active')

    column_labels = dict(
        id=lazy_gettext('id'),
        login=lazy_gettext('Login Name'),
        display=lazy_gettext('Display'),
        email=lazy_gettext('Email'),
        active=lazy_gettext('Active'),
        roles=lazy_gettext('Role')
    )

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    form_args = dict(
        active=dict(description=lazy_gettext('Un-check this checkbox to disable a user from login to the system')),
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
        form_class.password2 = PasswordField(label=lazy_gettext('New Password'),
                                             description=lazy_gettext('Left blank if you don\'t want to change it, '
                                                                      'input the new password to change it'))
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = generate_password_hash(model.password2)

# Customized Role model for SQL-Admin
class RoleAdmin(ModelViewWithAccess):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    column_list = ('id', 'name', 'description',)
    column_labels = dict(
        id=lazy_gettext('id'),
        name=lazy_gettext('Name'),
        description=lazy_gettext('Description'),
        users=lazy_gettext('User')
    )
    column_editable_list = ('description',)