from psi.app.views import ModelViewWithAccess
from psi.app.views.formatter import supplier_formatter, product_formatter
from flask_babelex import lazy_gettext


class SupplierSalesReportAdmin(ModelViewWithAccess):
    can_edit = False
    can_delete = False
    can_create = False
    can_view_details = False

    column_default_sort = ('sales_profit', True)

    @property
    def role_identify(self):
        return "supplier_sales_report"

    column_searchable_list = ('name', 'mnemonic')

    column_list = ('name', 'sales_amount', 'sales_profit',
                   'daily_profit', 'daily_amount',)

    column_formatters = {
        'supplier': supplier_formatter,
        'product': product_formatter,
    }

    column_filters = {
        # 'sales_profit',
        # 'sales_date',
    }

    column_labels = {
        'name': lazy_gettext('Name'),
        'sales_profit': lazy_gettext('Sales Profit'),
        'sales_amount': lazy_gettext('Sales Amount'),
        'daily_profit': lazy_gettext('Daily Profit'),
        'daily_amount': lazy_gettext('Daily Amount'),
    }

    def get_query(self):
        return super(SupplierSalesReportAdmin, self)\
            .get_query().filter(self.model.sales_amount > 0)

    def get_count_query(self):
        return super(SupplierSalesReportAdmin, self)\
            .get_count_query().filter(self.model.sales_amount > 0)

    column_sortable_list = ('sales_profit', 'sales_amount', 'daily_profit',
                            'daily_amount',)
