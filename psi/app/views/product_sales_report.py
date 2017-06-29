from flask_babelex import lazy_gettext

from psi.app.models.product_sales import OverallProductSales, \
    LastMonthProductSales, YesterdayProductSales, LastWeekProductSales, \
    LastYearProductSales, LastQuarterProductSales, TodayProductSales, \
    ThisWeekProductSales, ThisMonthProductSales, ThisYearProductSales, \
    ThisQuarterProductSales
from psi.app.views.report_view_with_access import ReportViewWithAccess
from psi.app.utils import security_util


class ProductSalesReportAdmin(ReportViewWithAccess):

    column_default_sort = ('sales_profit', True)

    column_searchable_list = ('name', 'mnemonic')

    column_list = ('name', 'sales_amount', 'sales_profit', 'sales_quantity',
                   'daily_profit', 'daily_amount')

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
        overall=OverallProductSales,
        today=TodayProductSales,
        yesterday=YesterdayProductSales,
        this_week=ThisWeekProductSales,
        last_week=LastWeekProductSales,
        this_month=ThisMonthProductSales,
        last_month=LastMonthProductSales,
        this_year=ThisYearProductSales,
        last_year=LastYearProductSales,
        last_quarter=LastQuarterProductSales,
        this_quarter=ThisQuarterProductSales,
    )

    def get_list_columns(self):
        """
        This method is called instantly in list.html
        List of columns is decided runtime during render of the table
        Not decided during flask-admin blueprint startup.
        """
        columns = super(ProductSalesReportAdmin, self).get_list_columns()
        cols = ['sales_profit', 'daily_profit']
        columns = security_util.filter_columns_by_role(
            columns, cols,'purchase_price_view'
        )
        return columns

    report_type = 'today'

    column_formatters = {
    }

    column_filters = [
        'sales_profit',
        'sales_amount',
    ]

    column_labels = {
        'name': lazy_gettext('Name'),
        'sales_profit': lazy_gettext('Sales Profit'),
        'sales_amount': lazy_gettext('Sales Amount'),
        'sales_quantity': lazy_gettext('Sales Quantity'),
        'daily_profit': lazy_gettext('Daily Profit'),
        'daily_amount': lazy_gettext('Daily Amount'),
    }

    def get_query(self):
        return super(ProductSalesReportAdmin, self).get_query()\
            .filter(self.model.sales_amount > 0)

    def get_count_query(self):
        return super(ProductSalesReportAdmin, self).get_count_query()\
            .filter(self.model.sales_amount > 0)

    column_sortable_list = ('sales_profit', 'sales_amount', 'sales_quantity')
