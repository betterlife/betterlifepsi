# encoding=utf-8


def render_version():
    try:
        import os
        my_dir = os.path.dirname(os.path.realpath(__file__))
        with open(my_dir + '/../../swtag', 'r') as swtag:

            commit = b_num = b_date = b_id = branch = tag = ''
            builder_url = 'https://travis-ci.org/betterlife/psi/builds'
            git_url = 'https://github.com/betterlife/psi'

            [commit, b_num, b_id, branch, tag, b_date] = swtag.read().split(' ')
            if tag == '':
                tag = 'None'
            commit = commit[:7]
            build_url = "{builder_url}/{b_id}".format(builder_url=builder_url, b_id=b_id)
            b_link = '<a href="{build_url}" target="_blank">{b_num}</a>'.format(build_url=build_url, b_num=b_num)
            commit_url = "{git_url}/commit/{commit}".format(git_url=git_url, commit=commit)
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
    except IOError:
        result = 'Unknown Version(Local Development)'
    return result