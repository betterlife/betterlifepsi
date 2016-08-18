# coding=utf-8
import random

from faker import Faker
from flask.ext.login import current_user
import app.const as const

from app.utils import db_util

class ObjectFaker(object):
    def __init__(self):
        self.faker = Faker()

    def purchase_order(self, po_id=None, number_of_line=1, creator=current_user):
        from app.models import PurchaseOrder, PurchaseOrderLine, EnumValues
        po = PurchaseOrder()
        po.remark = self.faker.text()
        po.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2, right_digits=0)
        po.order_date = self.faker.date()
        po.status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
        po.id = po_id if po_id is not None else db_util.get_next_id(PurchaseOrder)
        po.organization = creator.organization
        po.supplier = self.supplier()
        for i in range(0, number_of_line):
            line = PurchaseOrderLine()
            line.remark = self.faker.text()
            line.id = i
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
        supplier.code = db_util.get_next_code(Supplier)
        supplier.can_mixed_whole_sale = self.faker.pybool()
        supplier.contact = self.faker.name()
        supplier.email = self.faker.email()
        supplier.phone = self.faker.phone_number()
        supplier.qq = self.faker.pyint()
        supplier.organization = creator.organization
        supplier.remark = self.faker.pystr(max_chars=100)
        supplier.website = self.faker.uri()[:64]
        return supplier

    def product(self, product_id=None, supplier=None, creator=current_user):
        from app.models import Product
        product = Product()
        product.id = product_id if product_id is not None else db_util.get_next_id(Product)
        product.category = self.category(creator=creator)
        product.code = db_util.get_next_code(Product)
        product.name = self.faker.name()
        product.deliver_day = random.randint(3, 7)
        product.supplier = self.supplier() if supplier is None else supplier
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

    def user(self):
        from app.models import User
        from flask_security.utils import encrypt_password
        user = User()
        user.active = True
        user.display = self.faker.name()
        user.email = self.faker.email()
        user.login = self.faker.name()
        password = self.faker.password()
        user.password = encrypt_password(password)
        user.organization = self.organization()
        return user, password

    def organization(self, organization_id = None):
        from app.models import Organization
        from app.models import EnumValues
        organization = Organization()
        organization.description = self.faker.text()
        organization.name = self.faker.name()
        result = db_util.get_result_raw_sql("select max(lft), max(rgt) from organization")

        organization.lft = result[0] + 1
        organization.rgt = result[1] + 1
        organization.id = organization_id if organization_id is not None else db_util.get_next_id(Organization)
        organization.type = EnumValues.find_one_by_code(u"DIRECT_SELLING_STORE")
        return organization

object_faker = ObjectFaker()
