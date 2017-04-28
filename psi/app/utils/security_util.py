# encoding=utf-8
from flask_babelex import gettext
from werkzeug.exceptions import abort

from psi.app.const import SUPER_ADMIN_ROLE_NAME
from flask_login import current_user

def exclude_super_admin_roles(name, query):
    """
    Filter out super admin related roles from role list page.
    :param name: Model name
    :param query: current query
    :return: filtered query
    """
    return query.filter(
        name != 'organization_view',
        name != 'organization_edit',
        name != 'organization_create',
        name != 'organization_delete',
        name != SUPER_ADMIN_ROLE_NAME)


def is_super_admin(user=current_user):
    """
    Whether a user is a cross organization super admin
    :param user: user to judge
    :return: True if the user is a super admin, otherwise False
    """
    return user is not None and user.has_role(SUPER_ADMIN_ROLE_NAME)


def get_user_roles(user=current_user):
    """
    Get all roles of a user, included derived roles not directly assigned to
    the user.
    :param user: user
    :return: A set of all roles assigned to the user
    """
    all_derive_roles = set()
    result = []
    if hasattr(user, 'roles'):
        for role in user.roles:
            all_derive_roles.add(
                get_all_sub_roles(role, current_result=all_derive_roles))
        for r in all_derive_roles:
            if r is not None:
                result.append(r)
    return result


def user_has_role(role, user=current_user):
    """
    Check whether a user has a specific role
    :param user: User
    :param role: Role to check
    :return:True if user has the role, otherwise False
    """
    user_roles = get_user_roles(user)
    return role in user_roles


def get_all_sub_roles(role, current_result):
    """
    Get all detail roles for a base role
    :param current_result: Current result
    :param role: Base Roles
    :return:list of all roles
    """
    if role.name not in current_result:
        current_result.add(role.name)
        for sr in role.sub_roles:
            current_result.add(get_all_sub_roles(sr, current_result))


def has_organization_field(obj):
    """
    To check whether this object has a organization field
    :param obj: object to check
    :return: True if organization field exists, otherwise false
    """
    return hasattr(obj, 'organization')


def is_root_organization(obj):
    """
    Check whether this object(organization) is the root organization
    This check is performed based on whether this org's parent org is None
    According to current design, only root organization's parent org could
    not None
    :param obj: object to check
    :return: True if it's root organization, otherwise false
    """
    return obj is not None and obj.parent is None


def filter_columns_by_role(columns, to_filter_cols, role):
    """
    Filter columns based on user's role
    :param columns: Columns to be filtered
    :param to_filter_cols: columns to remove if user does not have that role
    :param role: User need this role to show the to_filter_cols
    :return: A filtered column list
    """
    new_col_list = []
    local_user = current_user._get_current_object()
    if (not user_has_role(role, local_user)):
        for l in columns:
            if l[0] not in to_filter_cols:
                new_col_list.append(l)
        columns = tuple(new_col_list)
    return columns


def return_error_as_json():
    """
    Return 403 error information as a dict(and possible render as json)
    :return:
    """
    return dict(message=gettext("You don't have permission to do this action"), status='error'), 403


def default_action_on_error():
    """
    Default action on 403 error
    :return:
    """
    abort(403)