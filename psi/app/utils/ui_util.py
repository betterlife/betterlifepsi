# encoding=utf-8
import time
from flask import current_app
import os

default_swtag_file = os.path.dirname(os.path.realpath(__file__)) + '/../../swtag'


def has_inline_field(form):
    for f in form:
        if is_inline_field(f):
            return True
    return False


def is_inline_field(field):
    from flask_admin.contrib.sqla.form import InlineModelFormList
    r = isinstance(field, InlineModelFormList)
    return r

def render_version(swtag_file=default_swtag_file):
    try:
        builder_url = current_app.config['BUILDER_URL_PREFIX']
        git_url = current_app.config['GIT_URL_PREFIX']

        line = open(swtag_file, 'r').readline()
        [commit, b_num, b_id, branch, tag, b_date] = line.split(' ')
        if tag == '':
            tag = 'None'
        commit = commit[:7]
        build_url = "{builder_url}/{b_id}".format(builder_url=builder_url, b_id=b_id)
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
