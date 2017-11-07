# coding=utf-8
from psi.app.utils import user_has_role, format_util
from flask import url_for, render_template
from flask_babelex import lazy_gettext
from markupsafe import Markup

from psi.app.views.views_mapping import get_endpoint_by_type_attr

has_invoice_field = {'label': lazy_gettext('Has Invoice'), 'field': 'has_invoice'}
goods_amount_field = {'label': lazy_gettext('Goods Amount'), 'field': 'goods_amount'}
unit_price_field = {'label': lazy_gettext('Unit Price'), 'field': 'unit_price'}
price_field = {'label': lazy_gettext('Unit Price'), 'field': 'price'}
code_field = {'label': lazy_gettext('Code'), 'field': 'code'}
lead_day_field = {'label': lazy_gettext('Lead Day'), 'field': 'lead_day'}
deliver_day_field = {'label': lazy_gettext('Deliver Day'), 'field': 'deliver_day'}
spec_link_field = {'label': lazy_gettext('Spec Link'), 'field': 'spec_link'}
distinguishing_feature_field = {'label': lazy_gettext('Distinguishing Feature'), 'field': 'distinguishing_feature'}
retail_price_field = {'label': lazy_gettext('Retail Price'), 'field': 'retail_price'}
price_discount_field = {'label': lazy_gettext('Price Discount'), 'field': 'price_discount'}
quantity_field = {"label": lazy_gettext('Quantity'), "field": 'quantity'}
in_transit_quantity_field = {"label": lazy_gettext('In Transit Quantity'), "field": 'in_transit_quantity'}
product_field = {'label': lazy_gettext('Product'), 'field': 'product'}
logistic_amount_field = {'label': lazy_gettext('Logistic Amount'), 'field': 'logistic_amount'}
actual_amount_field = {'label': lazy_gettext('Actual Amount'), 'field': 'actual_amount'}
original_amount_field = {'label': lazy_gettext('Original Amount'), 'field': 'original_amount'}
discount_amount_field = {'label': lazy_gettext('Discount Amount'), 'field': 'discount_amount'}
total_amount_field = {'label': lazy_gettext('Total Amount'), 'field': 'total_amount'}
category_field = {'label': lazy_gettext('Category'), 'field': 'category'}
remark_field = {'label': lazy_gettext('Remark'), 'field': 'remark'}
status_field = {'label': lazy_gettext('Status'), 'field': 'status'}
type_field = {'label': lazy_gettext('Type'), 'field': 'type'}
amount_field = {'label': lazy_gettext('Total Amount'), 'field': 'amount'}
date_field = {'label': lazy_gettext('Date'), 'field': 'date'}
order_date_field = {'label': lazy_gettext('Order Date'), 'field': 'order_date'}
order_status_field = {'label': lazy_gettext('Order Status'), 'field': 'status'}
order_type_field = {'label': lazy_gettext('Order Type'), 'field': 'type'}
id_field = {'label': lazy_gettext('Id'), 'field': 'id'}
supplier_field = {'label': lazy_gettext('Supplier'), 'field': 'supplier'}
name_field = {'label': lazy_gettext('Name'), 'field': 'name'}
saleable_quantity_field = {'label': lazy_gettext('Saleable Quantity'), 'field': 'saleable_quantity'}


def boolean_formatter(val_to_format):
    if val_to_format is None:
        return ''
    if isinstance(val_to_format, bool):
        if val_to_format is True:
            val_to_format = '<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>'
        else:
            val_to_format = '<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>'
    return val_to_format


def _obj_formatter_str(view, context, model, value=None, model_name=None, title=None, fields=None,
                       detail_fields=None, detail_field=None):

    endpoint = get_endpoint_by_type_attr(value, model_name)

    header, detail_labels, detail_lines = [],[],[]
    for k in fields:
        field = {}
        val = getattr(value, str(k['field']))
        field['label'] = k['label']
        field['value'] = str(boolean_formatter(val))
        header.append(field)

    detail_val = getattr(value, detail_field) if detail_field is not None else None
    if detail_val is not None and len(detail_val) > 0:
        for detail_key in detail_fields:
            detail_labels.append(detail_key['label'])
        for detail_line_val in detail_val:
            line_vals = []
            for detail_key in detail_fields:
                val = str(boolean_formatter(getattr(detail_line_val, detail_key['field'])))
                line_vals.append(val)
            detail_lines.append(line_vals)
    return render_template('components/object_ref.html',
                           title = title, value = value, endpoint=endpoint,
                           header = header, detail_labels = detail_labels,
                           detail_lines = detail_lines)


def _obj_formatter(view, context, model, value=None, model_name=None, title=None, fields=None,
                   detail_fields=None, detail_field=None):
    str_markup = _obj_formatter_str(view, context, model, value, model_name, title, fields,
                                    detail_fields, detail_field)
    return Markup(str_markup)


def _objs_formatter(view, context, model, values, model_name, title_field='id', fields=None,
                    detail_fields=None, detail_field=None):
    idx = 0
    result = ''
    if values is not None and len(values) > 0:
        for s in values:
            if s is not None:
                if idx != 0:
                    result += ', '
                idx += 1
                title = getattr(s, title_field)
                result += _obj_formatter_str(view, context, model, s, model_name, title, fields,
                                             detail_fields, detail_field)
    return Markup(result)


def supplier_formatter(view, context, model, name):
    try:
        s = model.supplier
    except Exception:
        s = model

    fields = (name_field,
            {'label': lazy_gettext('QQ'), 'field': 'qq'},
            {'label': lazy_gettext('Phone'), 'field': 'phone'},
            {'label': lazy_gettext('Contact'), 'field': 'contact'},
            {'label': lazy_gettext('Email'), 'field': 'email'},
            {'label': lazy_gettext('Whole Sale Req'), 'field': 'whole_sale_req'},
            {'label': lazy_gettext('Can Mixed Whole Sale'), 'field': 'can_mixed_whole_sale'},
            remark_field,)
    detail_fields = (
        {'label': '开户名', 'field': 'account_name'},
        {'label': '账户号', 'field': 'account_number'},
        {'label': '开户行', 'field': 'bank_name'},
        {'label': '分行', 'field': 'bank_branch'},
    )
    if s is not None:
        return _obj_formatter(view, context, model, value=s, model_name='supplier',
                              title=s.name, fields=fields, detail_fields=detail_fields, detail_field='paymentMethods')
    return ''


def expenses_formatter(view, context, model, name):
    if hasattr(model, 'expenses'):
        expenses = model.expenses
    else:
        expenses = [model.expense]
    fields = (date_field, amount_field, has_invoice_field, status_field, category_field, remark_field)
    return _objs_formatter(view, context, model, values=expenses, model_name='expense', fields=fields)


def receivings_formatter(view, context, model, name):
    if hasattr(model, 'po_receivings'):
        receivings = model.po_receivings
    elif hasattr(model, 'it_receiving'):
        receivings = [model.it_receiving]
    else:
        receivings = [model.po_receivings]
    if user_has_role('purchase_price_view'):
        fields = (date_field, total_amount_field, status_field, remark_field,)
        detail_fields = (product_field, quantity_field, price_field, total_amount_field)
    else:
        fields = (date_field, status_field, remark_field,)
        detail_fields = (product_field, quantity_field)
    return _objs_formatter(view, context, model, values=receivings, model_name='receiving',
                           fields=fields, detail_field='lines', detail_fields=detail_fields)


def incoming_formatter(view, context, model, name):
    i = model.incoming
    if i is not None:
        fields = (amount_field, date_field, category_field, status_field, remark_field,)
        return _obj_formatter(view, context, model, value=i, model_name='incoming',
                              title=str(i.id) + ' - ' + str(i.amount), fields=fields)
    return ''


def shipping_formatter(view, context, model, name):
    s = None
    if hasattr(model, 'so_shipping'):
        s = model.so_shipping
    elif hasattr(model, 'it_shipping'):
        s = model.it_shipping
    if s is not None:
        fields = (date_field, status_field, total_amount_field, remark_field,)
        detail_fields = (product_field, quantity_field, price_field, total_amount_field)
        return _obj_formatter(view, context, model, value=s, model_name='shipping', title=str(s.id),
                              fields=fields, detail_fields=detail_fields, detail_field='lines')
    return ''


def purchase_order_formatter(view, context, model, name):
    s = model.purchase_order
    if s is not None:
        if user_has_role('purchase_price_view'):
            fields = (order_type_field, order_status_field, order_date_field, supplier_field,
                    goods_amount_field, total_amount_field, remark_field)
            detail_fields = (product_field, quantity_field, unit_price_field, total_amount_field)
        else:
            fields = (order_type_field, order_status_field, order_date_field, supplier_field, remark_field)
            detail_fields = (product_field, quantity_field)
        return _obj_formatter(view, context, model, value=s, model_name='purchaseorder', title=str(s.id),
                              fields=fields, detail_fields=detail_fields, detail_field='lines')
    return ''


def sales_order_formatter(view, context, model, name):
    s = model.sales_order
    if s is not None:
        fields = (order_type_field, order_status_field, order_date_field, logistic_amount_field, actual_amount_field,
                discount_amount_field, original_amount_field, remark_field)
        detail_fields = (product_field, quantity_field, unit_price_field, retail_price_field, price_discount_field,
                       discount_amount_field, actual_amount_field, original_amount_field,)
        return _obj_formatter(view, context, model, value=s, model_name='salesorder', title=str(s.id),
                              fields=fields, detail_fields=detail_fields, detail_field='lines')
    return ''


def inventory_transaction_formatter(view, context, model, name):
    s = model.inventory_transaction
    if s is not None:
        if user_has_role('purchase_price_view'):
            fields = (date_field, type_field, total_amount_field, remark_field,)
            detail_fields = (product_field, in_transit_quantity_field, quantity_field, price_field,
                           total_amount_field, remark_field)
        else:
            fields = (date_field, type_field, remark_field,)
            detail_fields = (product_field, in_transit_quantity_field, quantity_field, remark_field)
        return _obj_formatter(view, context, model, value=s, model_name='inventorytransaction', title=str(s.id),
                              fields=fields, detail_fields=detail_fields, detail_field='lines')
    return ''


def product_formatter(view, context, model, name):
    fields = (lead_day_field, deliver_day_field, supplier_field, category_field, spec_link_field,
            distinguishing_feature_field)
    return _obj_formatter(view, context, model, value=model, model_name='product', title=model.name, fields=fields)


def organization_formatter(view, context, model, name):
    fields = (name_field,)
    obj = getattr(model, name)
    if obj is not None:
        if type(obj) is list:
            return _objs_formatter(view, context, model, values=obj, title_field='name', model_name='organization', fields=fields)
        return _obj_formatter(view, context, model, value=obj, title=getattr(obj, 'name'), model_name='organization', fields=fields)
    return None


def default_date_formatter(view, context, model, name):
    value = getattr(model, name)
    if value is not None:
        return value.strftime("%Y-%m-%d")
    return ''


def available_quantity_formatter(view, context, model, name):
    value = getattr(model, name)
    if value < 0:
        return '<span class="a_q_error">' + str(value) + '</span>'
    elif value == 0:
        return '<span class="a_q_warning">' + str(value) + '</span>'
    else:
        return str(value)


def default_decimal_formatter(view, context, model, name):
    value = getattr(model, name)
    if value == 0 or value == 0.00 or value is None:
        return '-'
    return value


def rich_text_formatter(view, context, model, name):
    from wtforms.widgets import HTMLString
    value = getattr(model, name)
    return HTMLString(value)


def line_formatter(view, context, model, name):
    value = getattr(model, name)
    fields = view.line_fields
    labels, values = [],[]
    for field in fields:
        labels.append(field['label'])
    for line in value:
        line_val = []
        for f in fields:
            val = getattr(line, f['field'])
            line_val.append(str(boolean_formatter(val)))
        values.append(line_val)
    result = render_template('components/detail_lines.html',
                           detail_labels=labels,
                           detail_lines = values)
    return result


def percent_formatter(view, context, model, name):
    value = getattr(model, name)
    result = format_util.decimal_to_percent(value)
    return result
