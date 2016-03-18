# coding=utf-8
import StringIO
import csv
from datetime import datetime
from decimal import Decimal

from app import config
from app import const
from app.models import Supplier, Product, SalesOrder, SalesOrderLine, Shipping, ShippingLine, InventoryTransaction, \
    InventoryTransactionLine, EnumValues, Incoming, Preference
from app.utils import get_next_code, get_by_external_id, save_objects_commit, get_by_name
from flask import request
from flask.ext.admin import BaseView
from flask.ext.babelex import gettext
from flask.ext.login import login_required
from flask_admin import expose
from app.utils.decorations import has_role


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


def create_or_update_sales_order(po_num, po_line_num, product, ret_price, act_price, qty, sale_date):
    order = get_by_external_id(SalesOrder, po_num)
    if order is None:
        order = SalesOrder()
        order.external_id = po_num
        order.logistic_amount = 0
    order.order_date = sale_date
    existing = False
    line = None
    for line in order.lines:
        if line.external_id == po_line_num:
            existing = True
            break
    if not existing:
        line = SalesOrderLine()
        line.sales_order = order
        line.external_id = po_line_num
    line.unit_price = act_price
    line.quantity = qty
    line.product = product
    return order, line


def create_or_update_shipping(order, order_line, status):
    if order.so_shipping is not None:
        shipping = order.so_shipping
    else:
        shipping = Shipping()
        shipping.sales_order = order
        shipping.date = order.order_date
        shipping.status = status
    shipping_line = None
    existing = False
    for shipping_line in shipping.lines:
        if shipping_line.sales_order_line.external_id == order_line.external_id:
            existing = True
            break
    if not existing:
        shipping_line = ShippingLine()
        shipping_line.shipping = shipping
        shipping_line.sales_order_line = order_line
    shipping_line.product = order_line.product
    shipping_line.quantity = order_line.quantity
    shipping_line.price = order_line.unit_price
    return shipping, shipping_line


def create_or_update_inventory_transaction(shipping, shipping_line, it_type):
    if shipping.inventory_transaction is not None:
        it = shipping.inventory_transaction
    else:
        it = InventoryTransaction()
    it.date = shipping.date
    shipping.inventory_transaction = it
    it.type = it_type
    it_line = None
    existing = False
    for it_line in it.lines:
        if it_line.itl_shipping_line.sales_order_line.external_id == shipping_line.sales_order_line.external_id:
            existing = True
            break
    if not existing:
        it_line = InventoryTransactionLine()
        it_line.inventory_transaction = it
    shipping_line.inventory_transaction_line = it_line
    it_line.quantity = shipping_line.quantity
    it_line.product = shipping_line.product
    it_line.price = shipping_line.price
    return it, it_line


def create_or_update_incoming(order, order_line, incoming_category, incoming_status):
    if order.incoming is None:
        incoming = Incoming()
        incoming.amount = order_line.actual_amount
    else:
        incoming = order.incoming
        incoming.amount += order_line.actual_amount
    incoming.sales_order = order
    incoming.date = order.order_date
    incoming.category = incoming_category
    incoming.status = incoming_status
    return incoming


class ImportStoreDataView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    @has_role(['import_store_data'])
    def index(self):
        if request.method == 'GET':
            return self.render('data_loading/legacy.html')
        elif request.method == 'POST':
            content = request.form['content']
            f = StringIO.StringIO(content)
            reader = csv.reader(f, delimiter=',')
            line = 0
            shipping_status = EnumValues.find_one_by_code(const.SHIPPING_COMPLETE_STATUS_KEY)
            it_type = EnumValues.find_one_by_code(const.SALES_OUT_INV_TRANS_TYPE_KEY)
            incoming_category = Preference.get().def_so_incoming_type
            incoming_status = Preference.get().def_so_incoming_status
            for row in reader:
                if line != 0:  # Skip header line
                    # 订单编号(0), 订单行编号(1),商品编号(2),商品名称(3),供应商编号(4),供应商名称(5),进价(6),定价(7),卖价(8),价格折扣(9),数量(10),
                    # 金额(11),成本(12),毛利(13),折扣(%)(14),折扣额(15),毛利率(16),操作员(17),营业员(18),时间(19)
                    po_num, po_line_num, prd_num, prd_name, sup_num, sup_name, pur_price, ret_price, act_price, qty, s_date = \
                        row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(), \
                        Decimal(row[6].strip()), Decimal(row[7].strip()), Decimal(row[8].strip()), \
                        Decimal(row[10].strip()), datetime.strptime(row[19].strip(), '%Y-%m-%d %H:%M:%S.%f')

                    # 1. Create or update supplier --> return supplier
                    supplier = create_or_update_supplier(sup_num, sup_name)
                    # 2. Create or update product --> return product
                    product = create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier)
                    # 3. Create or update sales order / sales order line --> return PO.
                    order, order_line = create_or_update_sales_order(po_num, po_line_num, product, ret_price, act_price, qty, s_date)
                    # 4. Create shipping record --> return shipping id
                    shipping, shipping_line = create_or_update_shipping(order, order_line, shipping_status)
                    # 5. Create inventory transaction record --> return inventory transaction record
                    itr, itl = create_or_update_inventory_transaction(shipping, shipping_line, it_type)
                    # 6. Create related incoming and return it.
                    incoming = create_or_update_incoming(order, order_line, incoming_category, incoming_status)
                    save_objects_commit(supplier, product, order, shipping, itr, incoming)
                line += 1
            return gettext('Upload and import into system successfully')
