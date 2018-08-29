#coding=utf-8
from __future__ import print_function

import csv
import time
import traceback
import uuid
from datetime import datetime
from decimal import Decimal

import codecs
import os
import sys

from psi.app import const
from psi.app.models import Supplier, Product, SalesOrder, SalesOrderLine, Shipping, ShippingLine, InventoryTransaction, \
    InventoryTransactionLine, EnumValues, Incoming, PaymentMethod
from psi.app.utils import get_by_external_id, get_by_name, save_objects
from psi.app.utils.security_util import user_has_role
from flask import request, current_app
from flask_admin import BaseView
from flask_admin import expose
from flask_babelex import gettext
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from psi.app.utils.decorations import has_role
from psi.app.service import Info

db = Info.get_db()

def create_or_update_supplier(sup_num, sup_name, mem, contact, address,
                              email, phone, mobile,
                              remark, mobile2,
                              acct_name, acct_no):

    def concat(current_val, format_str, new_val):
        if new_val != '':
            val = format_str.format(new_val)
            if current_val == '':
                current_val += val
            else:
                current_val += ", " + val
        return current_val

    supplier = get_by_external_id(Supplier, sup_num)
    if supplier is None:
        supplier = get_by_name(Supplier, sup_name)
        if supplier is None:
            supplier = Supplier()
            supplier.organization_id = current_user.organization_id
            supplier.external_id = sup_num
            supplier.name = sup_name
            # TODO.xqliu Change this remark calculate to a reduce
            supplier.remark = concat('', "手机: {0}", mobile)
            supplier.remark = concat(supplier.remark, "手机2: {0}", mobile2)
            supplier.remark = concat(supplier.remark, "地址: {0}", address)
            supplier.remark = concat(supplier.remark, "备注: {0}", remark)
            supplier.contact = contact
            supplier.email = email
            supplier.phone = phone
            supplier.mnemonic = mem
            if acct_name is not None and acct_no is not None:
                pm = PaymentMethod()
                pm.account_name = acct_name
                pm.account_number = acct_no
                pm.bank_name = '-'
                pm.supplier = supplier
            db.session.add(supplier)
    return supplier


def create_or_update_product(prd_num, prd_name, prd_mem, pur_price, ret_price, supplier):
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
            prd.mnemonic = prd_mem
            prd.purchase_price = pur_price
            prd.retail_price = ret_price
            prd.supplier = supplier
            db.session.add(prd)
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


def strip_null(val):
    try:
        return Decimal(val)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        if val == 'NULL' or val == '':
            return Decimal(0)
        else:
            raise e


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
                    row = []
                    try:
                        for row in reader:
                            if line != 0:  # Skip header line
                                # 销售编号(0), 销售行编号(1), 商品编号(2), 商品名称(3), 商品简码(4),
                                # 供应商编号(5), 供应商名称(6), 供应商简码(7), 供应商联系人(8),
                                # 供应商地址(9), 供应商Email地址(10), 供应商电话(11), 供应商手机号码(12),
                                # 供应商账号名(13), 供应商账号编号(14), 供应商备注信息(15), 供应商手机号码2(16),
                                # 进价(17), 定价(18), 卖价(19), 价格折扣(20), 数量(21), 金额(22), 成本(23),
                                # 毛利(24), 折扣(%)(25), 折扣额(26), 毛利率(27), 操作员(28), 营业员(29), 时间(30)

                                if line % 100 == 0:
                                    current_time = int(time.time())
                                    time_spent = current_time - start_time
                                    print("Processed [{0}] lines within [{1}] seconds: \nContent: [{2}]".format(str(line), str(time_spent),",".join(row).decode('utf-8')))
                                s_row = list(map(lambda x: x.strip() if x != 'NULL' else '', row))
                                po_num, po_line_num = s_row[0], s_row[1]
                                prd_num, prd_name, prd_mem = s_row[2], s_row[3], s_row[4]
                                sup_num, sup_name, sup_mem = s_row[5], s_row[6], s_row[7]
                                sup_contact, sup_addr, sup_email, sup_tele, sup_mobile = s_row[8], s_row[9], s_row[10], s_row[11], s_row[12]
                                acct_name, acct_no, sup_remark, sup_mobile2 = s_row[13], s_row[14], s_row[15], s_row[16]
                                pur_price, ret_price, act_price = strip_null(s_row[17]), strip_null(s_row[18]), strip_null(s_row[19]),
                                qty, s_date = strip_null(s_row[21]), datetime.strptime(s_row[30], '%Y-%m-%d %H:%M:%S.%f')

                                line_exists = self.is_po_line_exists(po_num, po_line_num)
                                if not line_exists:
                                    imported_line += 1
                                    # 1. Create or update supplier --> return supplier
                                    supplier = create_or_update_supplier(sup_num, sup_name,
                                                                         mem=sup_mem, contact=sup_contact, address=sup_addr,
                                                                         email=sup_email, phone=sup_tele,
                                                                         mobile=sup_mobile, remark=sup_remark,
                                                                         mobile2=sup_mobile2, acct_name=acct_name, acct_no=acct_no)
                                    # 2. Create or update product --> return product
                                    product = create_or_update_product(prd_num, prd_name, prd_mem, pur_price, ret_price, supplier)
                                    # 3. Create or update sales order / sales order line --> return PO.
                                    order, order_line = create_or_update_sales_order(po_num, po_line_num, product, act_price, qty, s_date)
                                    # 4. Create shipping record --> return shipping id
                                    shipping, shipping_line = create_or_update_shipping(order, order_line, shipping_status)
                                    # 5. Create inventory transaction record --> return inventory transaction record
                                    itr, itl = create_or_update_inventory_transaction(shipping, shipping_line, it_type)
                                    # 6. Create related incoming and return it.
                                    incoming = create_or_update_incoming(order, order_line, incoming_category, incoming_status)
                                    save_objects((order, shipping, itr, incoming))
                                    db.session.commit()
                            line += 1
                        db.session.commit()
                        end_time = int(time.time())
                        time_spent = end_time - start_time
                        print ("Import of CSV data finished, imported line: {0}, time spent: {1} seconds"
                               .format(str(imported_line), time_spent))
                    except Exception as e:
                        try:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            print("Error to process line {0} in CSV file".format(line+1))
                            print ("Content of the line: \n\t" + ",".join(row).decode('utf-8'))
                            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
                        except Exception:
                            pass
                        return 'Upload and import failed in line [{0}] with error: {1} '.format(line, e.message)
                    return gettext('Upload and import into system successfully')

    def is_po_line_exists(self, po_num, po_line_num):
        existing_order = get_by_external_id(SalesOrder, po_num)
        if existing_order is not None:
            for line in existing_order.lines:
                if line.external_id == po_line_num:
                    return True
        return False
