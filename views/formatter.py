# coding=utf-8
from flask import url_for
from markupsafe import Markup

category_field = {'label': '分类', 'field': 'category'}
remark_field = {'label': '备注', 'field': 'remark'}
status_field = {'label': '状态', 'field': 'status'}
amount_field = {'label': '金额', 'field': 'amount'}
date_field = {'label': '时间', 'field': 'date'}
id_field = {'label': '编号', 'field': 'id'}

def _obj_formatter(view, context, model, value=None, model_name=None, title=None, args=None,
                   detail_args=None, detail_field=None):
    if value is not None:
        str_result = '<div class="row" style="margin-bottom:20px">'
        for k in args:
            str_result += '<div class="col-md-3">' + k['label'] + '</div><div class="col-md-9">' \
                          + str(getattr(value, k['field'])) + '</div>'
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
                        detail_str += '<td>' + str(getattr(detail_line_val, detail_key['field'])) + '</td>\n'
                    detail_str += '</tr>'
                detail_str += '</table>'
        str_result += detail_str
        return Markup(
            "<a href='%s' data-toggle='popover' title='[%s] 详情 <span style=\"float:right\"><a href=\"%s\" target=\"_blank\">编辑</a></span>' data-content='%s'>%s</a>"
            % ('#', title, url_for(model_name + '.edit_view', id=value.id), str_result, title)
        )
    return ''

def _objs_formatter(view, context, model, values, model_name, title_field=None, args=None):
    idx = 0
    result = ''
    if values is not None and len(values) > 0:
        for s in values:
            if s is not None:
                if idx != 0:
                    result += ', '
                idx += 1
                detail = '<div class="row">'
                for k in args:
                    detail += '<div class="col-md-3">' + k['label'] + '</div><div class="col-md-9">' + str(getattr(s, k['field'])) + '</div>'
                detail += '</div>'
                if title_field is not None:
                    title = str(getattr(s, title_field))
                else:
                    title = str(getattr(s, 'id'))
                result += Markup(
                    "<a href='%s' data-toggle='popover' title='[%s] 详情 <span style=\"float:right\"><a href=\"%s\" target=\"_blank\">编辑</a></span>' data-content='%s'>%s</a>"
                    % ('#', title, url_for(model_name + '.edit_view', id=s.id), detail, title)
                )
    return result

def supplier_formatter(view, context, model, name):
    s = model.supplier
    args = (id_field,
        {'label': '编码', 'field': 'code'},
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
    return _obj_formatter(view, context, model, value=s, model_name='supplier',
                          title=s.name, args=args, detail_args=detail_args, detail_field='paymentMethods')

def expenses_formatter(view, context, model, name):
    if hasattr(model, 'expenses'):
        expenses = model.expenses
    else:
        expenses = [model.expense]
    args = (id_field, date_field, amount_field, {'label': '发票', 'field': 'has_invoice'},
            status_field, category_field, remark_field)
    return _objs_formatter(view, context, model, values=expenses, model_name='expense', args=args)

def receivings_formatter(view, context, model, name):
    if hasattr(model, 'po_receivings'):
        receivings = model.po_receivings
    else:
        receivings = [model.po_receivings]
    args = (id_field, date_field, {'label': '金额', 'field': 'total_amount'}, status_field, remark_field,)
    return _objs_formatter(view, context, model, values=receivings, model_name='receiving', args=args)

def incoming_formatter(view, context, model, name):
    i = model.incoming
    if i is not None:
        args = (id_field, amount_field, date_field, category_field, status_field, remark_field,)
        return _obj_formatter(view, context, model, value=i, model_name='incoming',
                              title=str(i.id) + ' - ' + str(i.amount), args=args)
    return ''

def shipping_formatter(view, context, model, name):
    s = model.so_shipping
    if s is not None:
        args = (id_field, date_field, status_field, remark_field,)
        return _obj_formatter(view, context, model, value=s, model_name='incoming', title=str(s.id), args=args)
    return ''

def purchase_order_formatter(view, context, model, name):
    return ''