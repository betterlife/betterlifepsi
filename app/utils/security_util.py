# encoding=utf-8
from flask.ext.login import current_user


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
