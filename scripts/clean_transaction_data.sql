-- Clean all the transaction data
-- Please keep in mind the sequence of the statements do matters
-- Since they have foreign key relationship to others
delete from shipping_line;
delete from shipping;
delete from receiving_line;
delete from receiving;
delete from inventory_transaction_line;
delete from inventory_transaction;
delete from purchase_order_line;
delete from sales_order_line;
delete from expense;
delete from incoming;
delete from purchase_order;
delete from sales_order;