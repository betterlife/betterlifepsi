# encoding=utf-8
from psi.app.utils import db_util


def filter_by_organization(field, object_type):
    """
    Set field query for a edit or create form
    :param field: field to set the query
    :param object_type: object type to filter
    :return: field with query and _object_list set by the values
    """
    values = db_util.filter_by_organization(object_type)
    field.query = values
    # See https://github.com/flask-admin/flask-admin/issues/1261 for detail
    # issue.
    if len(values) == 0:
        field._object_list = []


def del_inline_form_field(inline_form, old_entries, field_name):
    """
    Delete a field from an inline form
    :param inline_form: the inline form from which the field will be deleted
    :param old_entries: Existing lines of the inline form
    :param field_name:  Name of the field to be deleted
    :return: None
    """
    # Delete field for new lines
    if hasattr(inline_form, field_name):
        delattr(inline_form, field_name)
    # Delete field for old lines
    for entry in old_entries:
        if hasattr(entry.form, field_name):
            delattr(entry.form, field_name)
        if hasattr(entry.form._fields, field_name):
            delattr(entry.form._fields, field_name)


def del_form_field(admin_def, form, field_name):
    """
    Delete a field from a form dynamically during runtime.
    :param admin_def: The admin object definition
    :param form: The generated form
    :param field_name:Name of the field to be deleted
    :return: None
    """
    if hasattr(form, field_name):
        delattr(form, field_name)
    if hasattr(form._fields, field_name):
        del form._fields[field_name]
    for f in form._unbound_fields:
        if f[0] == field_name:
            form._unbound_fields.remove(f)
            break
    if admin_def._form_edit_rules is not None:
        for r in admin_def._form_edit_rules:
            if r.field_name == field_name:
                admin_def._form_edit_rules.rules.remove(r)


def calc_inline_field_name(line_num, model_field):
    """
    Generate inline field name
    :param line_num:  Line number
    :param model_field: Model field name 
    :return: the inline field name in the UI form. 
    """
    return 'lines-{0}-{1}'.format(str(line_num), model_field)