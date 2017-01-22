# coding=utf-8
from app.utils import user_has_role
from flask import url_for
from flask_babelex import lazy_gettext
from markupsafe import Markup

from app.views.views_mapping import get_endpoint_by_type_attr

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
id_field = {'label': lazy_gettext('id'), 'field': 'id'}
supplier_field = {'label': lazy_gettext('Supplier'), 'field': 'supplier'}
name_field = {'label': lazy_gettext('Name'), 'field': 'name'}


def _obj_formatter_str(view, context, model, value=None, model_name=None, title=None, args=None,
                       detail_args=None, detail_field=None):
    def boolean_formatter(val_to_format):
        if isinstance(val_to_format, bool):
            if val_to_format is True:
                val_to_format = '<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>'
            else:
                val_to_format = '<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>'
        return val_to_format

    if value is not None:
        str_result = '<div class="row bottom-spacing">'
        for k in args:
            val = getattr(value, k['field'])
            if val is not None:
                val = boolean_formatter(val)
                str_result += '<div class="col-md-3">' + k['label'] + '</div><div class="col-md-9">' \
                              + str(val) + '</div>'
        detail_str = ''
        if detail_field is not None:
            detail_val = getattr(value, detail_field)
            str_result += '</div>'
            if detail_val is not None and len(detail_val) > 0:
                detail_str = '<table class="table table-striped table-bordered table-hover">'
                detail_str += '<tr>'
                for detail_key in detail_args:
                    detail_str += '<th>' + str(detail_key['label']) + '</th>\n'
                detail_str += '</tr>'
                for detail_line_val in detail_val:
                    detail_str += '<tr>'
                    for detail_key in detail_args:
                        val = str(boolean_formatter(getattr(detail_line_val, detail_key['field'])))
                        if val == 'None' or val is None:
                            val = ''
                        detail_str += '<td>' + val + '</td>\n'
                    detail_str += '</tr>'
                detail_str += '</table>'
        str_result += detail_str
        endpoint = get_endpoint_by_type_attr(value, model_name)
        if value.can_edit():
            edit_link = url_for(endpoint + '.edit_view', id=value.id)
            edit_link = """<a href="{link}" target="_blank"><span class="fa fa-pencil glyphicon glyphicon-pencil"></span></a>""".format(link=edit_link)
        else:
            edit_link = ''
        if value.can_view_details():
            detail_link = url_for(endpoint + '.details_view', id=value.id)
            detail_link = """<a href="{link}" target="_blank"><span class="fa fa-eye glyphicon glyphicon-eye-open"></span></a>&nbsp;&nbsp;""".format(link=detail_link)
        else:
            detail_link = ''
        title_link = """<span style="float:right">{dl}&nbsp;&nbsp;{el}</span>""".format(dl=detail_link, el=edit_link)
        return """<a style='cursor:help' data-toggle='popover' title='[ {t} ] 详情 {tr}' data-content='{dc}'>[ {t} ]</a>""".format(t=title, tr=title_link, dc=str_result)
    return ''


def _obj_formatter(view, context, model, value=None, model_name=None, title=None, args=None,
                   detail_args=None, detail_field=None):
    str_markup = _obj_formatter_str(view, context, model, value, model_name, title, args,
                                    detail_args, detail_field)
    return Markup(str_markup)


def _objs_formatter(view, context, model, values, model_name, title_field='id', args=None,
                    detail_args=None, detail_field=None):
    idx = 0
    result = ''
    if values is not None and len(values) > 0:
        for s in values:
            if s is not None:
                if idx != 0:
                    result += ', '
                idx += 1
                title = getattr(s, title_field)
                result += _obj_formatter_str(view, context, model, s, model_name, title, args,
                                             detail_args, detail_field)
    return Markup(result)


def supplier_formatter(view, context, model, name):
    s = model.supplier
    args = (id_field,
            {'label': '名称', 'field': 'name'},
            {'label': 'QQ', 'field': 'qq'},
            {'label': '电话', 'field': 'phone'},
            {'label': '联系人', 'field': 'contact'},
            {'label': '邮件', 'field': 'email'},
            {'label': '起批要求', 'field': 'whole_sale_req'},
            {'label': '可混批?', 'field': 'can_mixed_whole_sale'},
            remark_field,)
    detail_args = (
        id_field,
        {'label': '开户名', 'field': 'account_name'},
        {'label': '账户号', 'field': 'account_number'},
        {'label': '开户行', 'field': 'bank_name'},
        {'label': '分行', 'field': 'bank_branch'},
    )
    if s is not None:
        return _obj_formatter(view, context, model, value=s, model_name='supplier',
                              title=s.name, args=args, detail_args=detail_args, detail_field='paymentMethods')
    return ''


def expenses_formatter(view, context, model, name):
    if hasattr(model, 'expenses'):
        expenses = model.expenses
    else:
        expenses = [model.expense]
    args = (id_field, date_field, amount_field, has_invoice_field, status_field, category_field, remark_field)
    return _objs_formatter(view, context, model, values=expenses, model_name='expense', args=args)


def receivings_formatter(view, context, model, name):
    if hasattr(model, 'po_receivings'):
        receivings = model.po_receivings
    elif hasattr(model, 'it_receiving'):
        receivings = [model.it_receiving]
    else:
        receivings = [model.po_receivings]
    if user_has_role('purchase_price_view'):
        args = (id_field, date_field, total_amount_field, status_field, remark_field,)
        detail_args = (product_field, quantity_field, price_field, total_amount_field)
    else:
        args = (id_field, date_field, status_field, remark_field,)
        detail_args = (product_field, quantity_field)
    return _objs_formatter(view, context, model, values=receivings, model_name='receiving',
                           args=args, detail_field='lines', detail_args=detail_args)


def incoming_formatter(view, context, model, name):
    i = model.incoming
    if i is not None:
        args = (id_field, amount_field, date_field, category_field, status_field, remark_field,)
        return _obj_formatter(view, context, model, value=i, model_name='incoming',
                              title=str(i.id) + ' - ' + str(i.amount), args=args)
    return ''


def shipping_formatter(view, context, model, name):
    s = None
    if hasattr(model, 'so_shipping'):
        s = model.so_shipping
    elif hasattr(model, 'it_shipping'):
        s = model.it_shipping
    if s is not None:
        args = (id_field, date_field, status_field, total_amount_field, remark_field,)
        detail_args = (product_field, quantity_field, price_field, total_amount_field)
        return _obj_formatter(view, context, model, value=s, model_name='shipping', title=str(s.id),
                              args=args, detail_args=detail_args, detail_field='lines')
    return ''


def purchase_order_formatter(view, context, model, name):
    s = model.purchase_order
    if s is not None:
        if user_has_role('purchase_price_view'):
            args = (id_field, order_type_field, order_status_field, order_date_field, supplier_field,
                    goods_amount_field, total_amount_field, remark_field)
            detail_args = (product_field, quantity_field, unit_price_field, total_amount_field)
        else:
            args = (id_field, order_type_field, order_status_field, order_date_field, supplier_field, remark_field)
            detail_args = (product_field, quantity_field)
        return _obj_formatter(view, context, model, value=s, model_name='purchaseorder', title=str(s.id),
                              args=args, detail_args=detail_args, detail_field='lines')
    return ''


def sales_order_formatter(view, context, model, name):
    s = model.sales_order
    if s is not None:
        args = (id_field, order_type_field, order_status_field, order_date_field, logistic_amount_field, actual_amount_field,
                discount_amount_field, original_amount_field, remark_field)
        detail_args = (product_field, quantity_field, unit_price_field, retail_price_field, price_discount_field,
                       discount_amount_field, actual_amount_field, original_amount_field,)
        return _obj_formatter(view, context, model, value=s, model_name='salesorder', title=str(s.id),
                              args=args, detail_args=detail_args, detail_field='lines')
    return ''


def inventory_transaction_formatter(view, context, model, name):
    s = model.inventory_transaction
    if s is not None:
        if user_has_role('purchase_price_view'):
            args = (id_field, date_field, type_field, total_amount_field, remark_field,)
            detail_args = (product_field, in_transit_quantity_field, quantity_field, price_field,
                           total_amount_field, remark_field)
        else:
            args = (id_field, date_field, type_field, remark_field,)
            detail_args = (product_field, in_transit_quantity_field, quantity_field, remark_field)
        return _obj_formatter(view, context, model, value=s, model_name='inventorytransaction', title=str(s.id),
                              args=args, detail_args=detail_args, detail_field='lines')
    return ''


def product_formatter(view, context, model, name):
    args = (id_field, lead_day_field, deliver_day_field, supplier_field, category_field, spec_link_field,
            distinguishing_feature_field)
    return _obj_formatter(view, context, model, value=model, model_name='product', title=model.name, args=args)


def organization_formatter(view, context, model, name):
    args = (id_field, name_field)
    obj = getattr(model, name)
    if obj is not None:
        if type(obj) is list:
            return _objs_formatter(view, context, model, values=obj, title_field='name', model_name='organization', args=args)
        return _obj_formatter(view, context, model, value=obj, title=getattr(obj, 'name'), model_name='organization', args=args)
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
