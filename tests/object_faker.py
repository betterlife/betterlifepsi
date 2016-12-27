# coding=utf-8
import random

from faker import Faker
from flask.ext.login import current_user
import app.const as const

from app.utils import db_util


class ObjectFaker(object):
    def __init__(self):
        self.faker = Faker()

    def sales_order(self, so_id=None, number_of_line=1, creator=current_user, type=None):
        from app.models import SalesOrder, EnumValues, SalesOrderLine
        from app.const import SO_CREATED_STATUS_KEY, DIRECT_SO_TYPE_KEY
        so = SalesOrder()
        so.remark = self.faker.text()
        so.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2,
                                                right_digits=0)
        so.customer = self.customer(creator=creator)
        so.order_date = self.faker.date()
        created_status = EnumValues.find_one_by_code(SO_CREATED_STATUS_KEY)
        so.status_id = created_status.id
        if type is None:
            types = EnumValues.type_filter(const.SO_TYPE_KEY).all()
            so.type = random.choice(types)
        else:
            so.type = type
        so.id = so_id if so_id is not None else db_util.get_next_id(SalesOrder)
        for i in range(0, number_of_line):
            line = SalesOrderLine()
            line.remark = self.faker.text()
            line.id = db_util.get_next_id(SalesOrderLine)
            line.product = self.product(creator=creator)
            line.sales_order = so
            line.quantity = self.faker.pyint()
            line.unit_price = self.faker.pydecimal(positive=True,
                                                   left_digits=4,
                                                   right_digits=0)
        return so

    def purchase_order(self, po_id=None, number_of_line=1, creator=current_user):
        from app.models import PurchaseOrder, PurchaseOrderLine, EnumValues
        po = PurchaseOrder()
        po.remark = self.faker.text()
        po.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2, right_digits=0)
        po.order_date = self.faker.date()
        draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
        po.status_id = draft_status.id
        types = EnumValues.type_filter(const.PO_TYPE_KEY).all()
        po_type = random.choice(types)
        po.type_id = po_type.id
        po.id = po_id if po_id is not None else db_util.get_next_id(PurchaseOrder)
        po.organization = creator.organization
        po.supplier = self.supplier(creator=creator)
        for i in range(0, number_of_line):
            line = PurchaseOrderLine()
            line.remark = self.faker.text()
            line.id = db_util.get_next_id(PurchaseOrderLine)
            line.product = self.product(supplier=po.supplier, creator=creator)
            line.purchase_order = po
            line.quantity = self.faker.pyint()
            line.unit_price = self.faker.pydecimal(positive=True, left_digits=4, right_digits=0)
        return po

    def supplier(self, supplier_id=None, creator=current_user):
        from app.models import Supplier
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
        from app.models import Customer
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
        customer.points =self.faker.pyint()
        return customer

    def product(self, product_id=None, supplier=None, creator=current_user):
        from app.models import Product
        product = Product()
        product.id = product_id if product_id is not None else db_util.get_next_id(Product)
        product.category = self.category(creator=creator)
        product.name = self.faker.name()
        product.deliver_day = random.randint(3, 7)
        product.supplier = self.supplier(creator=creator) if supplier is None else supplier
        product.distinguishing_feature = self.faker.paragraphs(nb=3)
        product.lead_day = random.randint(1, 5)
        product.need_advice = self.faker.pybool()
        product.purchase_price = 20
        product.retail_price = 50
        product.organization = creator.organization
        return product

    def category(self, category_id=None, creator=current_user):
        from app.models import ProductCategory
        category = ProductCategory()
        category.id = category_id if category_id is not None else db_util.get_next_id(ProductCategory)
        category.code = self.faker.pystr(max_chars=8)
        category.name = self.faker.name()
        category.organization = creator.organization
        return category

    def user(self, role_names=None, organization=None):
        if role_names is None:
            role_names = []
        from app.models import User, Role
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
        from app.models import Organization
        from app.models import EnumValues
        organization = Organization()
        organization.description = self.faker.text()
        organization.name = self.faker.name()
        result = db_util.get_result_raw_sql("select max(lft), max(rgt) from organization")

        organization.lft = result[0] + 1
        organization.rgt = result[1] + 1
        organization.id = organization_id if organization_id is not None else db_util.get_next_id(Organization)
        if type is None:
            organization.type = EnumValues.find_one_by_code(u"DIRECT_SELLING_STORE")
        else:
            organization.type = type
        if parent is not None:
            organization.parent = parent
        return organization

object_faker = ObjectFaker()
