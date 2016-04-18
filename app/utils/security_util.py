# encoding=utf-8
from app.const import SUPER_ADMIN_ROLE_NAME
from flask.ext.login import current_user


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
    return user.has_role(SUPER_ADMIN_ROLE_NAME)


def get_user_roles(user=current_user):
    """
    Get all roles of a user, included derived roles not directly assigned to the user.
    :param user: user
    :return: A set of all roles assigned to the user
    """
    all_derive_roles = set()
    result = []
    for role in user.roles:
        all_derive_roles.add(get_all_sub_roles(role, current_result=all_derive_roles))
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
