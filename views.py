# coding=utf-8
import app_provider
from flask import url_for, request
from flask.ext.admin.babel import gettext
import flask_admin as admin
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from flask.ext.security import current_user, logout_user, login_user
from models import *
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import form, fields, validators
from flask_admin import helpers, expose


class ModelViewWithAccess(ModelView):
    def is_accessible(self):
        return self.can()

    @property
    def can_create(self):
        return self.can(operation='create')

    @property
    def can_delete(self):
        return self.can(operation='delete')

    @property
    def can_edit(self):
        return self.can(operation='edit')

    def can(self, operation='view'):
        tablename = self.model.__tablename__
        return current_user.is_authenticated() and (
            current_user.has_role('admin') or
            current_user.has_role(tablename + '_' + operation))

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated():
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class ProductCategoryAdmin(ModelViewWithAccess):
    column_exclude_list = ['sub_categories', 'products']

    column_sortable_list = ('id', 'code', 'name')
    column_searchable_list = ('code', 'name')
    # column_filters = ('code','name')
    column_editable_list = ['code', 'name']
    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'parent_category': lazy_gettext('Parent category'),
    }
    form_excluded_columns = ('sub_categories', 'products')


class ProductAdmin(ModelViewWithAccess):
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                            'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')

    # column_filters = column_searchable_list
    column_labels = {
        'supplier.name': lazy_gettext('Supplier Name'),
        'category.name': lazy_gettext('Category Name'),
        'category.code': lazy_gettext('Category Code'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'category': lazy_gettext('Category'),
        'deliver_day': lazy_gettext('Deliver Day'),
        'lead_day': lazy_gettext('Lead Day'),
        'distinguishing_feature': lazy_gettext('Distinguishing Feature'),
        'spec_link': lazy_gettext('Spec Link'),
        'purchase_price': lazy_gettext('Purchase Price'),
        'retail_price': lazy_gettext('Retail Price')
    }


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
    from models import PaymentMethod

    form_excluded_columns = ('purchaseOrders', 'products')
    inline_models = (PaymentMethodLineInlineAdmin(PaymentMethod),)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website',
                            'whole_sale_req', 'can_mixed_whole_sale', 'remark']
    column_searchable_list = ('code', 'name')
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
    }


class ReadOnlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(ReadOnlyStringField, self).__call__(**kwargs)


class PurchaseOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.total_amount = ReadOnlyStringField(label=lazy_gettext('Total Amount'))
        return form


class PurchaseOrderAdmin(ModelViewWithAccess):
    from models import PurchaseOrderLine

    column_list = ('id', 'logistic_amount', 'goods_amount',
                   'total_amount', 'order_date', 'supplier', 'all_expenses', 'remark')

    form_extra_fields = {
        "goods_amount": StringField(label=lazy_gettext('Goods Amount')),
        "total_amount": StringField(label=lazy_gettext('Total Amount')),
    }
    column_sortable_list = ('id', 'logistic_amount', 'total_amount',
                            'goods_amount', 'order_date', ('supplier', 'supplier.id'),)
    form_widget_args = {
        'goods_amount': {'disabled': True},
        'total_amount': {'disabled': True},
    }
    form_excluded_columns = ('expenses',)
    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'supplier': lazy_gettext('Supplier'),
        'remark': lazy_gettext('Remark'),
        'all_expenses': lazy_gettext('Related Expenses'),
        'total_amount': lazy_gettext('Total Amount'),
        'goods_amount': lazy_gettext('Goods Amount'),
        'lines': lazy_gettext('Lines'),
    }

    @staticmethod
    def create_expenses(model):
        expenses = model.expenses
        logistic_exp = None
        preference = Preference.get()
        goods_exp = None
        if expenses is None:
            expenses = dict()
        for expense in expenses:
            if (expense.category_id == preference.def_po_logistic_exp_type_id) and (model.logistic_amount != 0):
                logistic_exp = expense
                logistic_exp.amount = model.logistic_amount
            elif (expense.category_id == preference.def_po_goods_exp_type_id) and (model.goods_amount != 0):
                goods_exp = expense
                goods_exp.amount = model.goods_amount
        if (logistic_exp is None) and (model.logistic_amount != 0):
            logistic_exp = Expense(model.logistic_amount, model.order_date, preference.def_po_logistic_exp_status_id,
                                   preference.def_po_logistic_exp_type_id)
        if (goods_exp is None) and (model.goods_amount != 0):
            goods_exp = Expense(model.goods_amount, model.order_date, preference.def_po_goods_exp_status_id,
                                preference.def_po_goods_exp_type_id)
        logistic_exp.purchase_order_id = model.id
        goods_exp.purchase_order_id = model.id
        return logistic_exp, goods_exp

    inline_models = (PurchaseOrderLineInlineAdmin(PurchaseOrderLine),)

    def after_model_change(self, form, model, is_created):
        logistic_exp, goods_exp = PurchaseOrderAdmin.create_expenses(model)
        if logistic_exp is not None:
            app_provider.AppInfo.get_db().session.add(logistic_exp)
        if goods_exp is not None:
            app_provider.AppInfo.get_db().session.add(goods_exp)
        app_provider.AppInfo.get_db().session.commit()


class SalesOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.retail_price = ReadOnlyStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = ReadOnlyStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = ReadOnlyStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = ReadOnlyStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = ReadOnlyStringField(label=lazy_gettext('Discount Amount'))
        return form


class SalesOrderAdmin(ModelViewWithAccess):
    from models import SalesOrderLine

    column_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'remark')
    # column_filters = ('order_date', 'remark', 'logistic_amount')
    form_extra_fields = {
        'actual_amount': StringField(label=lazy_gettext('Actual Amount')),
        'original_amount': StringField(label=lazy_gettext('Original Amount')),
        'discount_amount': StringField(label=lazy_gettext('Discount Amount'))
    }
    form_widget_args = {
        'actual_amount': {'disabled': True},
        'original_amount': {'disabled': True},
        'discount_amount': {'disabled': True},
        'logistic_amount': {'default': 0}
    }
    form_excluded_columns = ('incoming', 'expense')
    column_sortable_list = ('id', 'logistic_amount', 'actual_amount',
                            'original_amount', 'discount_amount', 'order_date')
    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'remark': lazy_gettext('Remark'),
        'actual_amount': lazy_gettext('Actual Amount'),
        'original_amount': lazy_gettext('Original Amount'),
        'discount_amount': lazy_gettext('Discount Amount'),
        'incoming': lazy_gettext('Relate Incoming'),
        'expense': lazy_gettext('Relate Expense'),
        'lines': lazy_gettext('Lines'),
    }

    @staticmethod
    def create_incoming(model):
        incoming = model.incoming
        preference = Preference.get()
        incoming = SalesOrderAdmin.create_associated_obj(incoming, model, default_obj=Incoming(),
                                                         value=model.actual_amount,
                                                         status_id=preference.def_so_incoming_status_id,
                                                         type_id=preference.def_so_incoming_type_id)
        return incoming

    @staticmethod
    def create_expense(model):
        expense = model.expense
        preference = Preference.get()
        if (model.logistic_amount is not None) and (model.logistic_amount > 0):
            default_obj = Expense(model.logistic_amount, model.order_date,
                                  preference.def_so_exp_status_id, preference.def_so_exp_type_id)
            expense = SalesOrderAdmin.create_associated_obj(expense, model,
                                                            default_obj=default_obj,
                                                            value=model.logistic_amount,
                                                            status_id=preference.def_so_exp_status_id,
                                                            type_id=preference.def_so_exp_type_id)
        return expense

    @staticmethod
    def create_associated_obj(obj, model, default_obj, value, status_id, type_id):
        if obj is None:
            obj = default_obj
            obj.status_id = status_id
            obj.category_id = type_id
        obj.amount = value
        obj.sales_order_id = model.id
        obj.date = model.order_date
        return obj

    def after_model_change(self, form, model, is_created):
        incoming = SalesOrderAdmin.create_incoming(model)
        expense = SalesOrderAdmin.create_expense(model)
        if expense is not None:
            app_provider.AppInfo.get_db().session.add(expense)
        if incoming is not None:
            app_provider.AppInfo.get_db().session.add(incoming)
        app_provider.AppInfo.get_db().session.commit()


class IncomingAdmin(ModelViewWithAccess):
    column_list = ('id', 'date', 'amount', 'status', 'category', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount', ]

    form_args = dict(
        status=dict(query_factory=Incoming.status_filter),
        category=dict(query_factory=Incoming.type_filter),
    )
    column_sortable_list = ('id', 'date', 'amount', ('status', 'status.display'),
                            ('category', 'category.display'), 'remark')
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Relate Sales Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
    }
    # column_filters = ('date','amount','sales_order.remark', 'category.display')
    form_excluded_columns = ('sales_order',)


class ExpenseAdmin(ModelViewWithAccess):
    column_list = ('id', 'date', 'amount', 'has_invoice', 'status',
                   'category', 'purchase_order', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount', 'has_invoice', ]

    form_args = dict(
        status=dict(query_factory=Expense.status_filter),
        category=dict(query_factory=Expense.type_filter),
    )
    column_sortable_list = ('id', 'date', 'amount', 'has_invoice', ('status', 'status.display'),
                            ('category', 'category.display'), 'remark')
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Relate Sales Order'),
        'purchase_order': lazy_gettext('Relate Purchase Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
        'has_invoice': lazy_gettext('Has Invoice'),
    }
    # column_filters = ('has_invoice','date','amount','category.display',)
    form_excluded_columns = ('sales_order', 'purchase_order',)


class EnumValuesAdmin(ModelViewWithAccess):
    column_list = ('id', 'type', 'code', 'display',)

    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    # column_filters = ('code', 'display',)
    column_labels = {
        'id': lazy_gettext('id'),
        'type': lazy_gettext('Type'),
        'code': lazy_gettext('Code'),
        'display': lazy_gettext('Display'),
    }


class PreferenceAdmin(ModelViewWithAccess):
    can_create, can_delete = False, False

    form_args = dict(
        def_so_incoming_type=dict(query_factory=Incoming.type_filter),
        def_so_incoming_status=dict(query_factory=Incoming.status_filter),
        def_so_exp_status=dict(query_factory=Expense.status_filter),
        def_so_exp_type=dict(query_factory=Expense.type_filter),
        def_po_logistic_exp_status=dict(query_factory=Expense.status_filter),
        def_po_logistic_exp_type=dict(query_factory=Expense.type_filter),
        def_po_goods_exp_status=dict(query_factory=Expense.status_filter),
        def_po_goods_exp_type=dict(query_factory=Expense.type_filter),
    )
    column_list = ('def_so_incoming_type', 'def_so_incoming_status',
                   'def_so_exp_status', 'def_so_exp_type',
                   'def_po_logistic_exp_status', 'def_po_logistic_exp_type',
                   'def_po_goods_exp_status', 'def_po_goods_exp_type')
    column_labels = dict(
        def_so_incoming_type=lazy_gettext('Default Sales Order Incoming Type'),
        def_so_incoming_status=lazy_gettext('Default Sale Order Incoming Status'),
        def_so_exp_status=lazy_gettext('Default Sale Order Expense Status'),
        def_so_exp_type=lazy_gettext('Default Sales Order Expense Type'),
        def_po_logistic_exp_status=lazy_gettext('Default Purchase Order Logistic Expense Status'),
        def_po_logistic_exp_type=lazy_gettext('Default Purchase Order Logistic Expense Type'),
        def_po_goods_exp_status=lazy_gettext('Default Purchase Order Goods Expense Status'),
        def_po_goods_exp_type=lazy_gettext('Default Purchase Order Goods Expense Type'),
        remark=lazy_gettext('Remark'),
    )


# Customized User model for SQL-Admin
class UserAdmin(ModelViewWithAccess):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    column_list = ('id', 'login', 'display', 'email', 'active',)

    column_labels = dict(
        id=lazy_gettext('id'),
        login=lazy_gettext('Login Name'),
        display=lazy_gettext('Display'),
        email=lazy_gettext('Email'),
        active=lazy_gettext('Active'),
        roles=lazy_gettext('Role')
    )

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField(label=lazy_gettext('New Password'))
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = generate_password_hash(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(ModelViewWithAccess):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    column_list = ('id', 'name', 'description',)
    column_labels = dict(
        id=lazy_gettext('id'),
        name=lazy_gettext('Name'),
        description=lazy_gettext('Description'),
        users=lazy_gettext('User')
    )

class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()],
                               label=lazy_gettext('Login Name'), )
    password = fields.PasswordField(validators=[validators.required()],
                                    label=lazy_gettext('Password'))

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError(gettext('Invalid user'))

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError(gettext('Invalid password'))

        if not user.active:
            raise validators.ValidationError(gettext('User is disabled'))

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(AdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated():
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(AdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


def init_admin_views(app, db):
    db_session = db.session
    adminViews = Admin(app, lazy_gettext('Brand Name'), index_view=AdminIndexView(),
                       base_template='layout.html', template_mode='bootstrap3')
    adminViews.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, name=lazy_gettext("Purchase Order"),
                                           menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    adminViews.add_view(SalesOrderAdmin(SalesOrder, db_session, name=lazy_gettext("Sales Order"),
                                        menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    adminViews.add_view(ExpenseAdmin(Expense, db_session, name=lazy_gettext("Expense"),
                                     menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    adminViews.add_view(IncomingAdmin(Incoming, db_session, name=lazy_gettext("Incoming"),
                                      menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    adminViews.add_view(ProductAdmin(Product, db_session, name=lazy_gettext("Product"),
                                     menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    adminViews.add_view(SupplierAdmin(Supplier, db_session, name=lazy_gettext("Supplier"),
                                      menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(ProductCategoryAdmin(ProductCategory, db_session, name=lazy_gettext("Product Category"),
                                             menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    adminViews.add_view(EnumValuesAdmin(EnumValues, db_session, name=lazy_gettext("Enum Values"),
                                        menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    adminViews.add_view(PreferenceAdmin(Preference, db_session, name=lazy_gettext("Preference"),
                                        menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    adminViews.add_view(UserAdmin(User, db_session, name=lazy_gettext('User'),
                                  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(RoleAdmin(Role, db_session, name=lazy_gettext("Role"),
                                  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-eye-close'))
    return adminViews
