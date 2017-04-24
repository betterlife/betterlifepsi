from psi.app.reports.report import ReportApi


def init_report_endpoint(app, api):
    api.add_resource(ReportApi, '/api/reports/<string:report_type>/<string:report_period>')
