# coding=utf-8
import StringIO
import csv
from datetime import datetime
from decimal import Decimal
from app import config
from app.models import Supplier, Product, SalesOrder, SalesOrderLine
from app.utils import get_next_code, get_by_external_id, save_objects_commit

from flask import url_for, request
from flask.ext.admin import BaseView
from flask.ext.babelex import gettext
import flask_admin as admin
from flask.ext.security import current_user, \
    url_for_security
from werkzeug.utils import redirect
from flask_admin import expose


class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for_security('login'))
        return redirect(url_for('product_inventory.index_view'))


def create_or_update_supplier(sup_num, sup_name):
    supplier = get_by_external_id(Supplier, sup_num)
    if supplier is None:
        supplier = Supplier()
        supplier.code = get_next_code(Supplier)
        supplier.external_id = sup_num
    supplier.name = sup_name
    return supplier


def create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier):
    prd = get_by_external_id(Product, prd_num)
    if prd is None:
        prd = Product()
        prd.code = get_next_code(Product)
        prd.external_id = prd_num
        prd.deliver_day = config.DEFAULT_DELIVER_DAY
        prd.lead_day = config.DEFAULT_LEAD_DAY
        prd.category_id = config.DEFAULT_CATEGORY_ID
    prd.name = prd_name
    prd.purchase_price = pur_price
    prd.retail_price = ret_price
    prd.supplier = supplier
    return prd


def create_or_update_sales_order(po_num, product, act_price, qty, sale_date):
    order = get_by_external_id(SalesOrder, po_num)
    if order is None:
        order = SalesOrder()
        order.external_id = po_num
    order.order_date = sale_date
    existing = False
    for line in order.lines:
        if line.product.id == product.id:
            existing = True
            line.unit_price = act_price
            line.quantity = qty
            line.product = product
    if not existing:
        line = SalesOrderLine()
        line.sales_order = order
        line.unit_price = act_price
        line.quantity = qty
        line.product = product
    return order


class ImportStoreDataView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for_security('login'))
        if request.method == 'GET':
            return self.render('data_loading/legacy.html')
        elif request.method == 'POST':
            content = request.form['content']
            f = StringIO.StringIO(content)
            reader = csv.reader(f, delimiter=',')
            line = 0
            try:
                for row in reader:
                    if line != 0:  # Skip header line
                        # 销售编号(0),商品编号(1),商品名称(2),供应商编号(3),供应商名称(4),进价(5),定价(6),卖价(7),价格折扣(8),数量(9),
                        # 金额(10),成本(11),毛利(12),折扣(%)(13),折扣额(14),毛利率(15),操作员(16),时间(17)
                        po_num, prd_num, prd_name, sup_num, sup_name, pur_price, ret_price, act_price, qty, \
                        sale_date = \
                            row[0], row[1], row[2], row[3], row[4], Decimal(row[5]), Decimal(row[6]), Decimal(row[7]), \
                            Decimal(row[9]), datetime.strptime(row[17], '%Y-%m-%d %H:%M:%S.%f')

                        # 1. Create or update supplier --> return supplier
                        supplier = create_or_update_supplier(sup_num, sup_name)
                        # 2. Create or update product --> return product
                        product = create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier)
                        # 3. Create or update sales order / sales order line --> return PO.
                        order = create_or_update_sales_order(po_num, product, act_price, qty, sale_date)
                        # TODO Show error happens on which line and send the error to front end
                        save_objects_commit(supplier, product, order)
                    line += 1
            except Exception:
                message = u'导入第' + line + u'行时发生错误'
            else:
                message = gettext('Upload and import into system successfully')
            return message
