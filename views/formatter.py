# coding=utf-8
from flask import url_for
from markupsafe import Markup


def supplier_formatter(view, context, model, name):
    s = model.supplier
    detail_template = '<div class="row">' \
                      '<div class="col-md-3">编码</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">名称</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">QQ</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">电话</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">联系人</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">邮件</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">起批要求</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">可混批?</div><div class="col-md-9">%s</div>' \
                      '<div class="col-md-3">备注</div><div class="col-md-9">%s</div>' \
                      '</div>'
    detail = detail_template % (s.code, s.name, s.qq, s.phone, s.contact, s.email, s.whole_sale_req,
                                s.can_mixed_whole_sale, s.remark)
    return Markup(
        "<a href='%s' data-toggle='popover' title='供应商详情 <span style=\"float:right\"><a href=\"%s\" target=\"_blank\">Edit</a></span>' data-content='%s'>%s</a>"
        % ('#', url_for('supplier.edit_view', id=s.id), detail, s.name)
    )