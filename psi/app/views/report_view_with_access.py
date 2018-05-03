from .base import ModelViewWithAccess


class ReportViewWithAccess(ModelViewWithAccess):

    @property
    def role_identify(self):
        return "sales_report"

    can_edit = False
    can_delete = False
    can_create = False
    can_view_details = False
    page_size = 100

    report_type = None
    """
    Report type, this field is used to retrive report display name in UI and
    the backend model definition of the report.
    """

    sub_reports = []
    """
    Sub report lists, this is assume to be a list of tuple which points from 
    sub report type to the display of the sub report in UI.
    """

    report_models = dict()
    """
    Report models list which is assume to be a list of tuple which points from 
    sub report type to the backend model descripe the report fields
    """

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
