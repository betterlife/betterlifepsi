# coding=utf-8
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext
from app.views import ModelViewWithAccess
from app.views.custom_fields import ReadonlyStringField


class PaymentMethodLineInlineAdmin(InlineFormAdmin):
    # column_editable_list = ['account_name', 'account_number', 'bank_name', 'bank_branch', 'remark']
    form_args = dict(
        account_name=dict(label=lazy_gettext('Account Name')),
        account_number=dict(label=lazy_gettext('Account Number')),
        bank_name=dict(label=lazy_gettext('Bank Name')),
        bank_branch=dict(label=lazy_gettext('Bank Branch')),
        remark=dict(label=lazy_gettext('Remark')),
    )


class SupplierAdmin(ModelViewWithAccess):
    from app.models import PaymentMethod

    form_excluded_columns = ('purchaseOrders', 'products', 'organization')
    inline_models = (PaymentMethodLineInlineAdmin(PaymentMethod),)

    column_details_exclude_list = ('organization',)

    column_exclude_list = ('organization',)

    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website',
                            'whole_sale_req', 'can_mixed_whole_sale', 'remark']

    column_details_list = ['id', 'external_id', 'name', 'qq', 'phone', 'contact', 'email', 'website',
                           'whole_sale_req', 'can_mixed_whole_sale', 'remark', 'paymentMethods']

    column_searchable_list = ('code', 'name', 'external_id', 'name', 'qq', 'phone',
                              'contact', 'email', 'website', 'whole_sale_req', 'remark')

    column_filters = ('can_mixed_whole_sale',)

    form_overrides = dict(external_id=ReadonlyStringField)

    # column_filters = column_searchable_list
    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'qq': lazy_gettext('QQ'),
        'phone': lazy_gettext('Phone'),
        'contact': lazy_gettext('Contact'),
        'email': lazy_gettext('Email'),
        'website': lazy_gettext('Website'),
        'whole_sale_req': lazy_gettext('Whole Sale Req'),
        'can_mixed_whole_sale': lazy_gettext('Can Mixed Whole Sale'),
        'remark': lazy_gettext('Remark'),
        'paymentMethods': lazy_gettext('Payment Methods'),
        'external_id': lazy_gettext('External Id'),
    }
