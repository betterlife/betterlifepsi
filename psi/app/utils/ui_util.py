# encoding=utf-8
import time
from flask import current_app
import os


default_swtag_file = os.path.dirname(os.path.realpath(__file__)) + '/../../swtag'

def is_list_field(model, field):
    """
    Whether a field is a list field
    :param model:  Model of the field
    :param field: name of the field to check 
    :return: True if attribute with the name is a list field, False otherwise. 
    """
    import sqlalchemy
    return (type(getattr(model, field)) == sqlalchemy.orm.collections.InstrumentedList)\
        if hasattr(model, field) else False

def has_detail_field(form_or_view):
    """
    Whether a form or view has a inline field
    This is used in template to decide how to display the form 
    :param form_or_view: the admin form or admin view to check
    :return: True if has detail field, otherwise false 
    """
    if hasattr(form_or_view, 'line_fields'):
            line_fields = getattr(form_or_view, 'line_fields', None)
            if line_fields is not None:
                return len(line_fields) > 0
    else:
        try:
            for f in form_or_view:
                if is_inline_field(f):
                    return True
        except TypeError :
            return False


def is_inline_field(field):
    """
    Whether a field in create or edit form is an inline field
    :param field: THe field to check 
    :return: True if field is of instance InlineModelFormList, otherwise false 
    """
    from flask_admin.contrib.sqla.form import InlineModelFormList
    r = isinstance(field, InlineModelFormList)
    return r

def render_version(swtag_file=default_swtag_file):
    """
    Render version information in UI
    :param swtag_file:  swtag file which contains VCS and build information
    Of the follow format
    8ab8044c115edf5f14bccd4057a9b8e096c28f85 254 144799860 master V0.6.5 2016.7.14
    Where each part of the file is 
    * GIT commit hash
    * Build number in the build system
    * Internal build in the build system
    * Branch where the build been generated
    * Code tag number when the build been generated
    * Build date
    :return: 
    """
    try:
        builder_url = current_app.config['BUILDER_URL_PREFIX']
        git_url = current_app.config['GIT_URL_PREFIX']

        line = open(swtag_file, 'r').readline()
        [commit, b_num, b_id, branch, tag, b_date] = line.split(' ')
        if tag == '':
            tag = 'None'
        commit = commit[:7]
        build_url = "{builder_url}/{commit}".format(builder_url=builder_url, commit=commit)
        b_link = '<a href="{build_url}" target="_blank">{b_num}</a>'.format(build_url=build_url, b_num=b_num)
        commit_url = "{git_url}/{commit}".format(git_url=git_url, commit=commit)
        commit_link = '<a href="{commit_url}" target="_blank">{commit}</a>'.format(commit_url=commit_url, commit=commit)
        result = """Build: {b_link},
                    Commit: {commit_link},
                    Branch: {branch},
                    Tag: {tag},
                    Date: {b_date}""".format(b_link=b_link,
                                             b_date=b_date,
                                             commit_link=commit_link,
                                             branch=branch,
                                             tag=tag)
    except:
        result = 'Unknown Version(Local Development)'
    return result
