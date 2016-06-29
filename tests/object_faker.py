import random

from faker import Faker
from flask.ext.login import current_user
import app.const as const

from app.utils import db_util


class ObjectFaker(object):
    def __init__(self):
        self.faker = Faker()

    def purchase_order(self, po_id=None, number_of_line=1):
        from app.models import PurchaseOrder, PurchaseOrderLine, EnumValues
        po = PurchaseOrder()
        po.remark = self.faker.text()
        po.logistic_amount = self.faker.pyfloat(positive=True, left_digits=2, right_digits=0)
        po.order_date = self.faker.date_time_ad()
        po.status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
        po.id = po_id if po_id is not None else db_util.get_next_id(PurchaseOrder)
        po.supplier = self.supplier()
        for i in range(0, number_of_line):
            line = PurchaseOrderLine()
            line.remark = self.faker.text()
            line.id = i
            line.product = self.product(supplier=po.supplier)
            line.purchase_order = po
            line.quantity = self.faker.pyint()
            line.unit_price = self.faker.pydecimal(positive=True, left_digits=4, right_digits=0)
        return po

    def supplier(self, supplier_id=None):
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
        supplier.organization = current_user.organization
        supplier.remark = self.faker.pystr(max_chars=100)
        supplier.website = self.faker.uri()
        return supplier

    def product(self, product_id=None, supplier=None):
        from app.models import Product
        product = Product()
        product.id = product_id if product_id is not None else db_util.get_next_id(Product)
        product.category = self.category()
        product.code = db_util.get_next_code(Product)
        product.name = self.faker.name()
        product.deliver_day = random.randint(3, 7)
        product.supplier = self.supplier() if supplier is None else supplier
        product.distinguishing_feature = self.faker.paragraphs(nb=3)
        product.lead_day = random.randint(1, 5)
        product.need_advice = self.faker.pybool()
        product.purchase_price = 20
        product.retail_price = 50
        return product

    def category(self, category_id=None):
        from app.models import ProductCategory
        category = ProductCategory()
        category.id = category_id if category_id is not None else db_util.get_next_id(ProductCategory)
        category.code = self.faker.pystr(max_chars=8)
        category.name = self.faker.name()
        return category

object_faker = ObjectFaker()
