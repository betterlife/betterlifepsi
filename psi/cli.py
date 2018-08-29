from psi.wsgi import application


@application.cli.command()
def test():
    """Run the unit tests.
    "" python manage.py test
    """
    import subprocess
    return_code = subprocess.call("""nosetests tests \
            --with-coverage --cover-erase --cover-branches \
            --with-xunit --xunit-file=nosetests.xml""", shell=True)
    sys.exit(return_code)


@application.cli.command()
def generate_fake_order():
    """
    Load a set of fake data to the system
    * 10 Suppliers and customers
    * 5 purchase orders and sales_orders
    """
    from tests.object_faker import object_faker
    from psi.app.models import User
    from random import randint
    from psi.app.service import Info
    database = Info.get_db()
    user = database.session.query(User).get(1)
    for i in range(5):
        purchase_order = object_faker.purchase_order(creator=user, number_of_line=randint(1,9))
        sales_order = object_faker.sales_order(creator=user, number_of_line=randint(1, 9))
        database.session.add(purchase_order)
        database.session.add(sales_order)
    database.session.commit()


@application.cli.command()
def clean_transaction_data():
    """
    Clean all the transaction data, and keep all master data
    """
    # TODO.xqliu Disable clean of database for production
    from psi.app.service import Info
    database = Info.get_db()
    database.engine.execute("""
        DELETE FROM related_values;
        DELETE FROM inventory_in_out_link;
        DELETE FROM incoming;
        DELETE FROM shipping_line;
        DELETE FROM shipping;
        DELETE FROM expense;
        DELETE FROM receiving_line;
        DELETE FROM receiving;
        DELETE FROM purchase_order_line;
        DELETE FROM purchase_order;
        DELETE FROM sales_order_line;
        DELETE FROM sales_order;
        DELETE FROM inventory_transaction_line;
        DELETE FROM inventory_transaction;
        commit;
    """)

@application.cli.command()
def clean_database():
    """
    Clean the database and drop all the tables
    This only tested for postgresql at this moment
    """
    # TODO.xqliu Disable clean of database for production
    from psi.app.service import Info
    database = Info.get_db()
    database.engine.execute("""
        DROP VIEW sales_order_detail RESTRICT;
        ALTER TABLE related_values DROP CONSTRAINT related_values_relation_type_id_fkey;
        ALTER TABLE incoming DROP CONSTRAINT incoming_category_id_fkey;
        ALTER TABLE incoming DROP CONSTRAINT incoming_status_id_fkey;
        ALTER TABLE incoming DROP CONSTRAINT incoming_sales_order_id_fkey;
        ALTER TABLE incoming DROP CONSTRAINT incoming_organization_id_fkey;
        ALTER TABLE shipping_line DROP CONSTRAINT shipping_line_product_id_fkey;
        ALTER TABLE shipping_line DROP CONSTRAINT shipping_line_shipping_id_fkey;
        ALTER TABLE shipping_line DROP CONSTRAINT shipping_line_sales_order_line_id_fkey;
        ALTER TABLE shipping_line DROP CONSTRAINT shipping_line_inventory_transaction_line_id_fkey;
        ALTER TABLE payment_method DROP CONSTRAINT payment_method_supplier_id_fkey;
        ALTER TABLE expense DROP CONSTRAINT expense_status_id_fkey;
        ALTER TABLE expense DROP CONSTRAINT expense_category_id_fkey;
        ALTER TABLE expense DROP CONSTRAINT expense_purchase_order_id_fkey;
        ALTER TABLE expense DROP CONSTRAINT expense_sales_order_id_fkey;
        ALTER TABLE expense DROP CONSTRAINT expense_organization_id_fkey;
        ALTER TABLE roles_users DROP CONSTRAINT roles_users_user_id_fkey;
        ALTER TABLE roles_users DROP CONSTRAINT roles_users_role_id_fkey;
        ALTER TABLE product_image DROP CONSTRAINT product_image_product_id_fkey;
        ALTER TABLE product_image DROP CONSTRAINT product_image_image_id_fkey;
        ALTER TABLE receiving_line DROP CONSTRAINT receiving_line_product_id_fkey;
        ALTER TABLE receiving_line DROP CONSTRAINT receiving_line_receiving_id_fkey;
        ALTER TABLE receiving_line DROP CONSTRAINT receiving_line_purchase_order_line_id_fkey;
        ALTER TABLE receiving_line DROP CONSTRAINT receiving_line_inventory_transaction_line_id_fkey;
        ALTER TABLE shipping DROP CONSTRAINT shipping_status_id_fkey;
        ALTER TABLE shipping DROP CONSTRAINT shipping_sales_order_id_fkey;
        ALTER TABLE shipping DROP CONSTRAINT shipping_inventory_transaction_id_fkey;
        ALTER TABLE shipping DROP CONSTRAINT shipping_organization_id_fkey;
        ALTER TABLE shipping DROP CONSTRAINT shipping_type_id_fkey;
        ALTER TABLE purchase_order DROP CONSTRAINT purchase_order_supplier_id_fkey;
        ALTER TABLE purchase_order DROP CONSTRAINT purchase_order_status_id_fkey;
        ALTER TABLE purchase_order DROP CONSTRAINT purchase_order_organization_id_fkey;
        ALTER TABLE purchase_order DROP CONSTRAINT purchase_order_type_id_fkey;
        ALTER TABLE purchase_order DROP CONSTRAINT to_organization_id_fkey;
        ALTER TABLE sales_order DROP CONSTRAINT sales_order_customer_id_fkey;
        ALTER TABLE sales_order DROP CONSTRAINT sales_order_organization_id_fkey;
        ALTER TABLE sales_order DROP CONSTRAINT sales_order_type_id_fkey;
        ALTER TABLE sales_order DROP CONSTRAINT sales_order_status_id_fkey;
        ALTER TABLE receiving DROP CONSTRAINT receiving_status_id_fkey;
        ALTER TABLE receiving DROP CONSTRAINT receiving_purchase_order_id_fkey;
        ALTER TABLE receiving DROP CONSTRAINT receiving_inventory_transaction_id_fkey;
        ALTER TABLE receiving DROP CONSTRAINT receiving_organization_id_fkey;
        ALTER TABLE "user" DROP CONSTRAINT user_locale_id_fkey;
        ALTER TABLE "user" DROP CONSTRAINT user_timezone_id_fkey;
        ALTER TABLE "user" DROP CONSTRAINT user_organization_id_fkey;
        ALTER TABLE product DROP CONSTRAINT product_category_id_fkey;
        ALTER TABLE product DROP CONSTRAINT product_supplier_id_fkey;
        ALTER TABLE product DROP CONSTRAINT product_organization_id_fkey;
        ALTER TABLE customer DROP CONSTRAINT customer_join_channel_id_fkey;
        ALTER TABLE customer DROP CONSTRAINT customer_level_id_fkey;
        ALTER TABLE customer DROP CONSTRAINT customer_organization_id_fkey;
        ALTER TABLE purchase_order_line DROP CONSTRAINT purchase_order_line_purchase_order_id_fkey;
        ALTER TABLE purchase_order_line DROP CONSTRAINT purchase_order_line_product_id_fkey;
        ALTER TABLE product_category DROP CONSTRAINT product_category_parent_id_fkey;
        ALTER TABLE product_category DROP CONSTRAINT product_category_organization_id_fkey;
        ALTER TABLE inventory_transaction DROP CONSTRAINT inventory_transaction_type_id_fkey;
        ALTER TABLE inventory_transaction DROP CONSTRAINT inventory_transaction_organization_id_fkey;
        ALTER TABLE inventory_transaction_line DROP CONSTRAINT inventory_transaction_line_product_id_fkey;
        ALTER TABLE inventory_transaction_line DROP CONSTRAINT inventory_transaction_line_inventory_transaction_id_fkey;
        ALTER TABLE sales_order_line DROP CONSTRAINT sales_order_line_sales_order_id_fkey;
        ALTER TABLE sales_order_line DROP CONSTRAINT sales_order_line_product_id_fkey;
        ALTER TABLE supplier DROP CONSTRAINT supplier_organization_id_fkey;
        ALTER TABLE enum_values DROP CONSTRAINT enum_values_type_id_fkey;
        ALTER TABLE organization DROP CONSTRAINT organization_type_id_fkey;
        ALTER TABLE role DROP CONSTRAINT role_parent_id_fkey;
        DROP TABLE related_values;
        DROP TABLE inventory_in_out_link;
        DROP TABLE incoming;
        DROP TABLE shipping_line;
        DROP TABLE payment_method;
        DROP TABLE expense;
        DROP TABLE roles_users;
        DROP TABLE product_image;
        DROP TABLE receiving_line;
        DROP TABLE shipping;
        DROP TABLE purchase_order;
        DROP TABLE sales_order;
        DROP TABLE receiving;
        DROP TABLE "user";
        DROP TABLE product;
        DROP TABLE customer;
        DROP TABLE purchase_order_line;
        DROP TABLE product_category;
        DROP TABLE inventory_transaction;
        DROP TABLE inventory_transaction_line;
        DROP TABLE sales_order_line;
        DROP TABLE supplier;
        DROP TABLE enum_values;
        DROP TABLE organization;
        DROP TABLE role;
        DROP TABLE image;
        DROP TABLE alembic_version;
        commit;
    """)
