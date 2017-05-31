from flask_babelex import lazy_gettext

from psi.app.models.supplier_sales import OverallSupplierSales, \
    LastMonthSupplierSales, YesterdaySupplierSales, LastWeekSupplierSales
from psi.app.views.report_view_with_access import ReportViewWithAccess


# TODO.1 Sorting is not working
# TODO.2 Need to display translated report in UI
class SupplierSalesReportAdmin(ReportViewWithAccess):

    column_default_sort = ('sales_profit', True)

    @property
    def role_identify(self):
        return "supplier_sales_report"

    column_searchable_list = ('name', 'mnemonic')

    column_list = ('name', 'sales_amount', 'sales_profit',
                   'daily_profit', 'daily_amount')

    @property
    def sub_reports(self):
        reps = ['yesterday', 'last_week', 'last_month', 'last_quarter',
                'last_year', 'overall']
        return [(x, lazy_gettext(x.replace('_',' ').title())) for x in reps]

    report_models = dict(
        overall=OverallSupplierSales,
        last_month=LastMonthSupplierSales,
        yesterday=YesterdaySupplierSales,
        last_week=LastWeekSupplierSales,
    )

    report_type = 'yesterday'

    column_formatters = {
    }

    column_filters = [
        'sales_profit',
        'sales_amount',
        'daily_profit',
        'daily_amount',
    ]

    column_labels = {
        'name': lazy_gettext('Name'),
        'sales_profit': lazy_gettext('Sales Profit'),
        'sales_amount': lazy_gettext('Sales Amount'),
        'daily_profit': lazy_gettext('Daily Profit'),
        'daily_amount': lazy_gettext('Daily Amount'),
    }

    def get_query(self):
        return super(SupplierSalesReportAdmin, self).get_query()\
            .filter(self.model.sales_amount > 0)

    def get_count_query(self):
        return super(SupplierSalesReportAdmin, self).get_count_query()\
            .filter(self.model.sales_amount > 0)

    column_sortable_list = ('sales_profit', 'sales_amount', 'daily_profit',
                            'daily_amount',)
