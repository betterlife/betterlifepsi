# encoding=utf-8


def render_version():

    from flask import current_app

    lead_commit = 'build commit: '
    lead_number = 'build number: '
    lead_date = 'build date  : '
    lead_branch = 'build branch: '

    if current_app.config['DEBUG']:
        return "Local Development Environment"

    with open('swtag', 'r') as swtag:
        content = swtag.readlines()
        commit, build_number, build_date, branch = '', '', '', ''

        for line in content:
            if line.startswith(lead_commit):
                commit = line[len(lead_commit):].strip()[:6]
            elif line.startswith(lead_number):
                build_number = line[len(lead_number):].strip()
            elif line.startswith(lead_date):
                build_date = line[len(lead_date):].strip()
            elif line.startswith(lead_branch):
                branch = line[len(lead_branch):].strip()
    return """Build: <a href="http://devops.betterlife.io/viewLog.html?buildId={0}" target="_blank">{0}</a>, Date: {1}, Commit: <a href="https://github.com/betterlife/psi/commit/{2}" target="_blank">{2}</a>, Branch: {3}""".format(build_number, build_date, commit, branch)
