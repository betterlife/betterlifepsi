# coding=utf-8
import random

import psi.app.const as const
from psi.app.utils import db_util
from faker import Faker
from flask_login import current_user


class ObjectFaker(object):
    def __init__(self):
        self.faker = Faker()

    def sales_order(self, so_id=None, number_of_line=1, creator=current_user, type=None, products=None):
        from psi.app.models import SalesOrder, EnumValues, SalesOrderLine
        from psi.app.const import SO_CREATED_STATUS_KEY
        from psi.app.services import SalesOrderService
        so = SalesOrder()
        so.remark = self.faker.text(max_nb_chars=20)
        so.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2,
                                                right_digits=0)
        so.customer = self.customer(creator=creator)
        so.order_date = self.faker.date()
        created_status = EnumValues.get(SO_CREATED_STATUS_KEY)
        so.status_id = created_status.id
        so.organization = creator.organization
        if type is None:
            types = EnumValues.type_filter(const.SO_TYPE_KEY).all()
            so.type = random.choice(types)
        else:
            so.type = type
        so.id = so_id if so_id is not None else db_util.get_next_id(SalesOrder)
        for i in range(0, number_of_line):
            line = SalesOrderLine()
            line.remark = self.faker.text(max_nb_chars=10)
            line.id = db_util.get_next_id(SalesOrderLine)
            if products is None:
                line.product = self.product(creator=creator)
            else:
                line.product = products[i]
            line.sales_order = so
            line.quantity = random.randint(1, 100)
            line.unit_price = self.faker.pydecimal(positive=True,
                                                   left_digits=3,
                                                   right_digits=0)
        SalesOrderService.create_or_update_incoming(so)
        SalesOrderService.create_or_update_expense(so)
        return so

    def purchase_order(self, po_id=None, number_of_line=1, creator=current_user,
                       type=None, status=None):
        from psi.app.models import PurchaseOrder, PurchaseOrderLine, EnumValues
        po = PurchaseOrder()
        po.remark = self.faker.text(max_nb_chars=20)
        po.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2, right_digits=0)
        po.order_date = self.faker.date()
        if status is None:
            draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
            po.status = draft_status
        else:
            po.status = status
            po.status_id = status.id
        if type is None:
            types = EnumValues.type_filter(const.PO_TYPE_KEY).all()
            type = random.choice(types)
            if type.code == const.FRANCHISE_PO_TYPE_KEY:
                if creator.organization.parent is not None:
                    po.to_organization = creator.organization.parent
                else:
                    po.to_organization = creator.organization
        po.type = type
        po.type_id = type.id
        po.id = po_id if po_id is not None else db_util.get_next_id(PurchaseOrder)
        po.organization = creator.organization
        po.supplier = self.supplier(creator=creator)
        for i in range(0, number_of_line):
            line = PurchaseOrderLine()
            line.remark = self.faker.text(max_nb_chars=10)
            line.id = db_util.get_next_id(PurchaseOrderLine)
            line.product = self.product(supplier=po.supplier, creator=creator)
            line.purchase_order = po
            line.quantity = random.randint(1, 100)
            line.unit_price = self.faker.pydecimal(positive=True, left_digits=3, right_digits=0)
        return po

    def supplier(self, supplier_id=None, creator=current_user):
        from psi.app.models import Supplier
        supplier = Supplier()
        supplier.id = supplier_id if supplier_id is not None else db_util.get_next_id(Supplier)
        supplier.name = self.faker.name()
        supplier.can_mixed_whole_sale = self.faker.pybool()
        supplier.contact = self.faker.name()
        supplier.email = self.faker.email()
        supplier.phone = self.faker.phone_number()
        supplier.qq = self.faker.pyint()
        supplier.organization = creator.organization
        supplier.remark = self.faker.pystr(max_chars=100)
        supplier.website = self.faker.uri()[:64]
        return supplier

    def customer(self, customer_id=None, creator=current_user):
        from psi.app.models import Customer
        customer = Customer()
        customer.id = customer_id if customer_id is not None else db_util.get_next_id(Customer)
        customer.address = self.faker.address()
        customer.birthday = self.faker.date_time_this_decade()
        customer.email = self.faker.safe_email()
        customer.first_name = self.faker.first_name()
        customer.last_name = self.faker.last_name()
        customer.join_date = self.faker.date_time_this_decade()
        customer.join_channel = random.choice(customer.join_channel_filter().all())
        customer.level = random.choice(customer.level_filter().all())
        customer.organization = creator.organization
        customer.points = self.faker.pyint()
        return customer

    def product(self, product_id=None, supplier=None, creator=current_user):
        from psi.app.models import Product
        product = Product()
        product.id = product_id if product_id is not None else db_util.get_next_id(Product)
        product.category = self.category(creator=creator)
        product.name = self.faker.name()
        product.deliver_day = random.randint(3, 7)
        product.supplier = self.supplier(creator=creator) if supplier is None else supplier
        product.distinguishing_feature = self.faker.paragraphs(nb=3)
        product.lead_day = random.randint(1, 5)
        product.need_advice = self.faker.pybool()
        product.purchase_price = random.randint(1, 100)
        product.retail_price = product.purchase_price + random.randint(1, 100)
        product.organization = creator.organization
        return product

    def category(self, category_id=None, creator=current_user):
        from psi.app.models import ProductCategory
        category = ProductCategory()
        category.id = category_id if category_id is not None else db_util.get_next_id(ProductCategory)
        category.code = self.faker.pystr(max_chars=8)
        category.name = self.faker.name()
        category.organization = creator.organization
        return category

    def user(self, role_names=None, organization=None):
        if role_names is None:
            role_names = []
        from psi.app.models import User, Role
        from flask_security.utils import encrypt_password
        user = User()
        user.active = True
        user.display = self.faker.name()
        user.email = self.faker.email()
        user.login = self.faker.name()
        password = self.faker.password()
        user.password = encrypt_password(password)
        if organization is None:
            user.organization = self.organization()
        else:
            user.organization = organization
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            user.roles.append(role)
        return user, password

    def organization(self, organization_id = None, type=None, parent=None):
        from psi.app.models import Organization
        from psi.app.models import EnumValues
        organization = Organization()
        organization.description = self.faker.text(max_nb_chars=10)
        organization.name = self.faker.name()
        result = db_util.get_result_raw_sql("select max(lft), max(rgt) from organization")

        organization.lft = result[0] + 1
        organization.rgt = result[1] + 1
        organization.id = organization_id if organization_id is not None else db_util.get_next_id(Organization)
        if type is None:
            organization.type = EnumValues.get(u"DIRECT_SELLING_STORE")
        else:
            organization.type = type
        if parent is not None:
            organization.parent = parent
        return organization

object_faker = ObjectFaker()
