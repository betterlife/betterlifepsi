# encoding=utf-8


def render_version():
    try:
        with open('swtag', 'r') as swtag:

            lead_commit = 'build commit: '
            lead_number = 'build number: '
            lead_date = 'build date  : '
            lead_branch = 'build branch: '
            commit, build, build_date, branch = '', '', '', ''
            builder_url = 'http://devops.betterlife.io'
            git_url = 'https://github.com/betterlife/psi'

            content = swtag.readlines()
            for line in content:
                if line.startswith(lead_commit):
                    commit = line[len(lead_commit):].strip()[:6]
                elif line.startswith(lead_number):
                    build = line[len(lead_number):].strip()
                elif line.startswith(lead_date):
                    build_date = line[len(lead_date):].strip()
                elif line.startswith(lead_branch):
                    branch = line[len(lead_branch):].strip()
            build_url = "{builder_url}/viewLog.html?buildId={build}".format(builder_url=builder_url, build=build)
            build_link = "<a href=\"{build_url}\" target=\"_blank\">{build}</a>".format(build_url=build_url, build=build)
            commit_url = "{git_url}/commit/{commit}".format(git_url=git_url, commit = commit)
            commit_link = '<a href="{commit_url}" target="_blank">{commit}</a>'.format(commit_url=commit_url, commit=commit)
            branch_url = "{git_url}/tree/{branch}".format(git_url=git_url, branch=branch)
            branch_link = '<a href="{branch_url}" target="_blank">{branch}</a>'.format(branch_url=branch_url, branch=branch)
            result = """Build: {build_link}, Date: {build_date},
                     Commit: {commit_link}, Branch: {branch_link}""".format(build_link=build_link,
                                                                            build_date=build_date,
                                                                            commit_link=commit_link,
                                                                            branch_link=branch_link)
    except IOError:
        result = 'Unknown Version(Local Development)'
    return result
