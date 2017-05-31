from psi.app.views import ModelViewWithAccess


class ReportViewWithAccess(ModelViewWithAccess):
    can_edit = False
    can_delete = False
    can_create = False
    can_view_details = False
    page_size = 100
    report_type = None
    sub_reports = []
    report_models = dict()

    list_template = 'admin/report/list.html'

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        from flask import request
        self.report_type = request.args.get('type') \
            if request.args.get('type') is not None else self.report_type
        model_type = self.report_models.get(self.report_type)
        self.model = model_type if model_type is not None else self.model
        return super(ReportViewWithAccess, self).get_list(page, sort_column, sort_desc,
                                                   search, filters,
                                                   execute=True, page_size=None)
