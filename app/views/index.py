# coding=utf-8
import StringIO
import csv
from datetime import datetime
from decimal import Decimal
from app import config
from app.models import Supplier, Product, SalesOrder, SalesOrderLine
from app.utils import get_next_code, get_by_external_id, save_objects_commit, get_by_name

from flask import url_for, request, current_app
from flask.ext.admin import BaseView
from flask.ext.babelex import gettext
import flask_admin as admin
from flask.ext.security import current_user, url_for_security
from werkzeug.utils import redirect
from flask_admin import expose


class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for_security('login'))
        return redirect(url_for('product_inventory.index_view'))


def create_or_update_supplier(sup_num, sup_name):
    supplier = get_by_external_id(Supplier, sup_num)
    if supplier is None:
        supplier = get_by_name(Supplier, sup_name)
        if supplier is None:
            supplier = Supplier()
            supplier.code = get_next_code(Supplier)
        supplier.external_id = sup_num
    supplier.name = sup_name
    return supplier


def create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier):
    prd = get_by_external_id(Product, prd_num)
    if prd is None:
        prd = get_by_name(Product, prd_name)
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
        logger = current_app.logger
        if not current_user.is_authenticated:
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
                        # TODO How to strip each string element before join them?
                        logger.info("Start process line(%d) data: [%s]", line, ",".join(row))
                        # 销售编号(0),商品编号(1),商品名称(2),供应商编号(3),供应商名称(4),进价(5),定价(6),卖价(7),价格折扣(8),数量(9),
                        # 金额(10),成本(11),毛利(12),折扣(%)(13),折扣额(14),毛利率(15),操作员(16),时间(17)
                        po_num, prd_num, prd_name, sup_num, sup_name, pur_price, ret_price, act_price, qty, s_date = \
                            row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), \
                            Decimal(row[5].strip()), Decimal(row[6].strip()), Decimal(row[7].strip()), \
                            Decimal(row[9].strip()), datetime.strptime(row[17].strip(), '%Y-%m-%d %H:%M:%S.%f')

                        # 1. Create or update supplier --> return supplier
                        supplier = create_or_update_supplier(sup_num, sup_name)
                        # 2. Create or update product --> return product
                        product = create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier)
                        # 3. Create or update sales order / sales order line --> return PO.
                        order = create_or_update_sales_order(po_num, product, act_price, qty, s_date)
                        # 4. Create shipping record --> return shipping id
                        # 5. Create inventory transaction record --> return inventory transaction record
                        save_objects_commit(supplier, product, order)
                        logger.info('Finish process line %s', line)
                    line += 1
            except Exception, e:
                # FIXME How to return from an exception handler with a message and send the error to front end?
                message = u'导入第' + line + u'行时发生错误'
                pass
            else:
                message = gettext('Upload and import into system successfully')
            return message
