-- Clean the schema
drop table roles_users;
drop table role;
drop table "user";
drop table inventory_transaction_line;
drop table inventory_transaction;
drop table shipping_line;
drop table shipping;
drop table receiving_line;
drop table receiving;
drop table purchase_order_line;
drop table sales_order_line;
drop table expense;
drop table incoming;
drop table purchase_order;
drop table sales_order;
drop table customer;
drop table product;
drop table payment_method;
drop table supplier;
drop table product_category;
drop table preference;
drop table enum_values;
drop table alembic_version;

-- Update patch version automatically
-- update alembic_version set version_num = '29b31f4d8de6'
