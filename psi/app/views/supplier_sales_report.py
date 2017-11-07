from flask_babelex import lazy_gettext

from psi.app.models.supplier_sales import OverallSupplierSales, \
    LastMonthSupplierSales, YesterdaySupplierSales, LastWeekSupplierSales, \
    LastYearSupplierSales, LastQuarterSupplierSales, TodaySupplierSales, \
    ThisWeekSupplierSales, ThisMonthSupplierSales, ThisYearSupplierSales, \
    ThisQuarterSupplierSales
from psi.app.views.formatter import supplier_formatter, percent_formatter
from psi.app.views.report_view_with_access import ReportViewWithAccess
from psi.app.utils import security_util


class SupplierSalesReportAdmin(ReportViewWithAccess):

    column_default_sort = ('sales_profit', True)

    @property
    def role_identify(self):
        return "sales_report"

    column_searchable_list = ('name', 'mnemonic')

    column_list = ('name', 'sales_amount', 'sales_profit',
                   'daily_profit', 'daily_amount', 'sales_profit_percentage')

    def get_list_columns(self):
        """
        This method is called instantly in list.html
        List of columns is decided runtime during render of the table
        Not decided during flask-admin blueprint startup.
        """
        columns = super(SupplierSalesReportAdmin, self).get_list_columns()
        cols = ['sales_profit', 'daily_profit']
        columns = security_util.filter_columns_by_role(
            columns, cols,'purchase_price_view'
        )
        return columns

    @property
    def sub_reports(self):
        reps = ['overall',
                'today', 'yesterday',
                'this_week', 'last_week',
                'this_month', 'last_month',
                'this_quarter', 'last_quarter',
                'this_year', 'last_year',]
        return [(x, lazy_gettext(x.replace('_',' ').title())) for x in reps]

    report_models = dict(
        overall=OverallSupplierSales,
        today=TodaySupplierSales,
        yesterday=YesterdaySupplierSales,
        this_week=ThisWeekSupplierSales,
        last_week=LastWeekSupplierSales,
        this_month=ThisMonthSupplierSales,
        last_month=LastMonthSupplierSales,
        this_year=ThisYearSupplierSales,
        last_year=LastYearSupplierSales,
        last_quarter=LastQuarterSupplierSales,
        this_quarter=ThisQuarterSupplierSales,
    )

    report_type = 'today'

    column_formatters = {
        'name': supplier_formatter,
        'sales_profit_percentage': percent_formatter,
    }

    column_filters = ['sales_amount', 'daily_amount',]

    column_labels = {
        'sales_profit': lazy_gettext('Sales Profit'),
        'sales_amount': lazy_gettext('Sales Amount'),
        'daily_profit': lazy_gettext('Daily Profit'),
        'daily_amount': lazy_gettext('Daily Amount'),
        'sales_profit_percentage': lazy_gettext('Sales Profit Percentage'),
    }

    def get_query(self):
        # Only displays supplier with profit larger than 1%
        return super(SupplierSalesReportAdmin, self).get_query()\
            .filter(self.model.sales_profit_percentage > 0.01)

    def get_count_query(self):
        return super(SupplierSalesReportAdmin, self).get_count_query()\
            .filter(self.model.sales_profit_percentage > 0.01)

    column_sortable_list = ('sales_profit', 'sales_amount', 'daily_profit',
                            'daily_amount',)
