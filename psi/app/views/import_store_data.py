#coding=utf-8
from __future__ import print_function

import csv
import time
import uuid
from datetime import datetime
from decimal import Decimal

import codecs
import os
from psi.app import const
from psi.app.models import Supplier, Product, SalesOrder, SalesOrderLine, Shipping, ShippingLine, InventoryTransaction, \
    InventoryTransactionLine, EnumValues, Incoming
from psi.app.utils import get_by_external_id, save_objects_commit, get_by_name
from psi.app.utils.security_util import user_has_role
from flask import request, current_app
from flask_admin import BaseView
from flask_admin import expose
from flask_babelex import gettext
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from psi.app.utils.decorations import has_role


def create_or_update_supplier(sup_num, sup_name):
    supplier = get_by_external_id(Supplier, sup_num)
    if supplier is None:
        supplier = get_by_name(Supplier, sup_name)
        if supplier is None:
            supplier = Supplier()
            supplier.organization_id = current_user.organization_id
        supplier.external_id = sup_num
    supplier.name = sup_name
    return supplier


def create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier):
    prd = get_by_external_id(Product, prd_num)
    if prd is None:
        prd = get_by_name(Product, prd_name)
        if prd is None:
            prd = Product()
        prd.external_id = prd_num
        prd.deliver_day = current_app.config.get('DEFAULT_DELIVER_DAY')
        prd.lead_day = current_app.config.get('DEFAULT_LEAD_DAY')
        prd.category_id = current_app.config.get('DEFAULT_CATEGORY_ID')
        prd.organization_id = current_user.organization_id
    prd.name = prd_name
    prd.purchase_price = pur_price
    prd.retail_price = ret_price
    prd.supplier = supplier
    return prd


def create_or_update_sales_order(po_num, po_line_num, product, act_price, qty, sale_date):
    order = get_by_external_id(SalesOrder, po_num)
    if order is None:
        order = SalesOrder()
        order.external_id = po_num
        order.logistic_amount = 0
        order.organization_id = current_user.organization_id
    order.order_date = sale_date
    order.type = EnumValues.get(const.DIRECT_SO_TYPE_KEY)
    order.status = EnumValues.get(const.SO_DELIVERED_STATUS_KEY)
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
        shipping.organization_id = current_user.organization_id
        shipping.type = EnumValues.get(const.DIRECT_SHIPPING_TYPE_KEY)
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
        it.organization_id = current_user.organization_id
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
    it_line.quantity = -shipping_line.quantity
    it_line.product = shipping_line.product
    it_line.price = shipping_line.price
    return it, it_line


def create_or_update_incoming(order, order_line, incoming_category, incoming_status):
    if order.incoming is None:
        incoming = Incoming()
        incoming.amount = order_line.actual_amount
        incoming.organization_id = current_user.organization_id
    else:
        incoming = order.incoming
        incoming.amount += order_line.actual_amount
    incoming.sales_order = order
    incoming.date = order.order_date
    incoming.category = incoming_category
    incoming.status = incoming_status
    return incoming


class ImportStoreDataView(BaseView):
    def is_accessible(self):
        return user_has_role('import_store_data')

    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    @has_role('import_store_data')
    def index(self):
        if request.method == 'GET':
            return self.render('data_loading/legacy.html')
        elif request.method == 'POST':
            start_time = int(time.time())
            csv_file = request.files['file']
            if csv_file:
                filename = secure_filename(csv_file.filename)
                if len(filename) == 0:
                    filename = str(uuid.uuid4())
                full_path = os.path.join(current_app.config['UPLOAD_TMP_FOLDER'], filename)
                csv_file.save(full_path)
                with codecs.open(full_path, 'rb', 'UTF-8') as f:
                    reader = csv.reader(f, delimiter=',')
                    line, imported_line = 0,0
                    shipping_status = EnumValues.get(const.SHIPPING_COMPLETE_STATUS_KEY)
                    it_type = EnumValues.get(const.SALES_OUT_INV_TRANS_TYPE_KEY)
                    incoming_category = EnumValues.get(const.DEFUALT_SALES_ORDER_INCOMING_TYPE_KEY)
                    incoming_status = EnumValues.get(const.DEFUALT_SALES_ORDER_INCOMING_STATUS_KEY)
                    for row in reader:
                        if line != 0:  # Skip header line
                            # 订单编号(0), 订单行编号(1),商品编号(2),商品名称(3),供应商编号(4),供应商名称(5),进价(6),定价(7),卖价(8),价格折扣(9),数量(10),
                            # 金额(11),成本(12),毛利(13),折扣(%)(14),折扣额(15),毛利率(16),操作员(17),营业员(18),时间(19)
                            if line % 100 == 0:
                                print("Processing line: [{0}]\nContent: [{1}]".format(str(line), ",".join(row).decode('utf-8')))
                            po_num, po_line_num, prd_num, prd_name, sup_num, sup_name, pur_price, ret_price, act_price, qty, s_date = \
                                row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(), \
                                Decimal(row[6].strip()), Decimal(row[7].strip()), Decimal(row[8].strip()), \
                                Decimal(row[10].strip()), datetime.strptime(row[19].strip(), '%Y-%m-%d %H:%M:%S.%f')
                            line_exists = self.is_po_line_exists(po_num, po_line_num)
                            if  not line_exists:
                                imported_line += 1
                                # 1. Create or update supplier --> return supplier
                                supplier = create_or_update_supplier(sup_num, sup_name)
                                # 2. Create or update product --> return product
                                product = create_or_update_product(prd_num, prd_name, pur_price, ret_price, supplier)
                                # 3. Create or update sales order / sales order line --> return PO.
                                order, order_line = create_or_update_sales_order(po_num, po_line_num, product, act_price, qty, s_date)
                                # 4. Create shipping record --> return shipping id
                                shipping, shipping_line = create_or_update_shipping(order, order_line, shipping_status)
                                # 5. Create inventory transaction record --> return inventory transaction record
                                itr, itl = create_or_update_inventory_transaction(shipping, shipping_line, it_type)
                                # 6. Create related incoming and return it.
                                incoming = create_or_update_incoming(order, order_line, incoming_category, incoming_status)
                                save_objects_commit(supplier, product, order, shipping, itr, incoming)
                        line += 1
                    end_time = int(time.time())
                    time_spent = end_time - start_time
                    print ("Import of CSV data finished, imported line: {0}, time spent: {1} seconds"
                           .format(str(imported_line), time_spent))
                    return gettext('Upload and import into system successfully')

    def is_po_line_exists(self, po_num, po_line_num):
        existing_order = get_by_external_id(SalesOrder, po_num)
        if existing_order is not None:
            for line in existing_order.lines:
                if line.external_id == po_line_num:
                    return True
        return False