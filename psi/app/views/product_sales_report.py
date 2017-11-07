from flask_babelex import lazy_gettext

from psi.app.models.product_sales import OverallProductSales, \
    LastMonthProductSales, YesterdayProductSales, LastWeekProductSales, \
    LastYearProductSales, LastQuarterProductSales, TodayProductSales, \
    ThisWeekProductSales, ThisMonthProductSales, ThisYearProductSales, \
    ThisQuarterProductSales
from psi.app.views.formatter import supplier_formatter, percent_formatter
from psi.app.views.report_view_with_access import ReportViewWithAccess
from psi.app.utils import security_util


class ProductSalesReportAdmin(ReportViewWithAccess):

    column_default_sort = ('sales_profit', True)

    column_searchable_list = ('name', 'mnemonic', 'supplier.name',
                              'supplier.mnemonic')

    column_list = ('name', 'supplier', 'sales_amount', 'sales_profit',
                   'sales_quantity', 'daily_profit', 'daily_amount',
                   'sales_profit_percentage')

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
        'supplier': supplier_formatter,
        'sales_profit_percentage': percent_formatter,
    }

    column_filters = ['sales_profit', 'sales_amount',]

    column_labels = {
        'name': lazy_gettext('Name'),
        'mnemonic': lazy_gettext('Product Mnemonic'),
        'supplier.name': lazy_gettext('Supplier'),
        'supplier.mnemonic': lazy_gettext('Supplier Mnemonic'),
        'sales_profit': lazy_gettext('Sales Profit'),
        'sales_amount': lazy_gettext('Sales Amount'),
        'sales_quantity': lazy_gettext('Sales Quantity'),
        'daily_profit': lazy_gettext('Daily Profit'),
        'daily_amount': lazy_gettext('Daily Amount'),
        'sales_profit_percentage': lazy_gettext('Sales Profit Percentage'),
    }

    def get_query(self):
        # Only displays product with profit larger than 0.1%
        return super(ProductSalesReportAdmin, self).get_query()\
            .filter(self.model.sales_profit_percentage > 0.001)

    def get_count_query(self):
        return super(ProductSalesReportAdmin, self).get_count_query()\
            .filter(self.model.sales_profit_percentage > 0.001)

    column_sortable_list = ('supplier.name', 'sales_profit', 'sales_amount',
                            'sales_quantity',)
