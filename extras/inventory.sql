------------------------------------------------------------------ALL_TABLES_creation

--products

CREATE TABLE product(
  ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR2(50),
  price integer,
  capacity NUMBER,
  description varchar(200),
  img varchar(200),
  rackid number;
  CONSTRAINT rack_f1 FOREIGN KEY (rackid) REFERENCES racks(id)
);

--notification
CREATE TABLE notifications (
    notno NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message VARCHAR2(200),
    cusid NUMBER,
    aid NUMBER,
    CONSTRAINT fgk FOREIGN KEY (cusid) REFERENCES customer (id),
    CONSTRAINT fgjk FOREIGN KEY (aid) REFERENCES admin (id)
);
--racks

CREATE TABLE racks (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 quantity number
);

--customer

create table customer(
fname varchar(20),
lname varchar(20),
id number GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
address varchar(40),
email varchar(20) unique,
wallet integer
);

--admin

create table admin(
fname varchar(20),
lname varchar(20),
id number GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
email varchar(20) unique
);

--vendor

create table vendor(
lname varchar(20),
fname varchar(20),
id number GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
address varchar(40),
email varchar(20) unique
);



--vendor products

create table vendor_products(
pid number,
quantity integer,
vid number,
constraint fg foreign key(pid) references products(id),
constraint fg1 foreign key(vid) references vendor(id),
primary key(pid,vid)
);

--customer cart

CREATE TABLE cuscart (
  cart_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id NUMBER,
  product_id NUMBER,
  quantity INTEGER,
  FOREIGN KEY (id) REFERENCES customer(id),
  FOREIGN KEY (product_id) REFERENCES products(ID)
);

--sales

create table sales(
order_no number,
cusid number,
productid number,
perunit_price integer,
quantity number,
date_ti date,
constraints fk81 foreign key(cusid) references customer(id),
constraints fk84 foreign key(productid) references products(id)
);


--purchase

create table purchase(
purchase_no number,
vendorid number,
productid number,
cost_price integer,
quantity number,
dat date,
constraints fk1 foreign key(vendorid) references vendor(id),
constraints fk21 foreign key(productid) references products(id)
);



--admin cart

CREATE TABLE admincart (
  cart_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id NUMBER,
  quantity INTEGER,
  vid number,
  aid number
);

--admin products

create table admin_products(
pid number,
quantity integer,
constraint gfhe foreign key(pid) references products(id)
);


------------------------------------------------------------------plsql

--admin checkout
create or replace procedure checkout
is 
nu number:=0;
pi number;
qu number;
cursor rt is select p.cart_id,p.product_id,p.quantity,p.vid,p.aid,p1.price from admincart p,products p1 where p1.id=p.product_id;
begin
----
nu := adm.nextval;
for i in rt
loop
update admin_products
set quantity = quantity + i.quantity
where pid=i.product_id;
if sql%notfound
then insert into admin_products values(i.product_id,i.quantity,i.price*1.12);
end if;
end loop;
insert into purchase(purchase_no,vendorid,productid,cost_price,quantity,dat) select nu,p.vid,p.product_id,p1.price,p.quantity,SYSDATE from admincart p,products p1 where p.product_id=p1.id;
delete from admincart;
end;


--customer checkout

create or replace procedure cuscheckout
is 
nu number:=0;
begin
nu := cusc.nextval;
insert into sales (order_no,cusid,productid,quantity,perunit_price,date_ti) select nu, p.id,p.product_id,p.quantity,p.price,SYSDATE from cuscart p , products p1 where p1.id=p.product_id ;
delete from cuscart;
end;

--vendor qty

CREATE OR REPLACE PROCEDURE vendorqty(vi NUMBER, pi NUMBER, qty NUMBER) IS
  flg NUMBER := 0;
BEGIN
  SELECT vid INTO flg FROM vendor_products WHERE vid = vi AND pid = pi;

  UPDATE vendor_products
  SET quantity = quantity + qty
  WHERE vid = vi AND pid = pi;

  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO vendor_products VALUES(pi, qty, vi);
END;

--admincart

create or replace procedure addadmincart(pi number,vi number,qty number,ai number)
is
vqty number:=0;
v number;
begin
select quantity into vqty from vendor_products where pid=pi and vid=vi;
update vendor_products 
set quantity = quantity - qty
where pid=pi and vid=vi;
select vid into v from admincart where vid=vi and product_id = pi;
update admincart 
set quantity= quantity + qty
where vid=vi and product_id=pi;
EXCEPTION
    WHEN NO_DATA_FOUND THEN insert into admincart(product_id,quantity,vid,aid) values(pi,qty,vi,ai);
end;

--rem admin cart

create or replace procedure remadmincart(cart_i number)
is
ctid number;
pi number;
vi number;
qty number;
flg number;
begin
select product_id,quantity,vid into pi,qty,vi from admincart where cart_id=cart_i;
select vid into flg from vendor_products where vid = vi and pid = pi;

update vendor_products
set quantity = quantity + qty
where vid=vi and pid=pi;
delete from admincart where cart_id = cart_i;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
    insert into vendor_products values(pi,qty,vi);
    delete from admincart where cart_id = cart_i;


end;

--cuscart

create or replace procedure addcuscart(pi number,ci number,qty number)
is
vqty number:=0;
v number;
prc NUMBER;
begin
select price into prc from admin_products where pi=pid;
update admin_products 
set quantity = quantity - qty
where pid=pi ;
select product_id into v from cuscart where product_id=pi;
update cuscart
set quantity=quantity + qty
where product_id=pi;
EXCEPTION
    WHEN NO_DATA_FOUND THEN 
    insert into cuscart(product_id,quantity,id,price) values(pi,qty,ci,prc);
end;

--rem cus cart

create or replace procedure remcuscart(cart_i number)
is
pi number;
qty number;
flg number;
prc number;
begin
select product_id,quantity,price into pi,qty,prc from cuscart where cart_id=cart_i;
select pid into flg from admin_products where pid = pi;

update admin_products
set quantity = quantity + qty
where pid=pi;
delete from cuscart where cart_id = cart_i;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
    insert into admin_products values(pi,qty,prc);
    delete from cuscart where cart_id = cart_i;


end;


--notification

create or replace procedure p1
is
v varchar(20);
cid number;
cursor ri is select idp,ono from cusmsg;
begin
for i in ri
loop
select email into v from customer where id=i.idp;
insert into notifications(message,cemail,aid) values('THANK YOU FOR YOUR PURCHASE(THIS IS AUTO GENERATED MESSAGE)',v,'f219294@admin.edu.pk');
update sales
set bool=1
where cusid=i.idp;
end loop;
end;


----------------------------------------------------------------sequence

create sequence cusc start with 1 increment by 1

create sequence adm start with 1 increment by 1

------------------------------------------------------------------view

--sales history

create view sales_his as select order_no order_id,cusid customerid,date_ti datee,sum(quantity) totalqty,sum(quantity * perunit_price) totalrs from sales group by order_no,date_ti,cusid;

--puchase history

create view purchase_his as select purchase_no puid,sum(quantity * cost_price) total,dat datee,sum(quantity) tqty from purchase group by purchase_no,dat;

--rack view found item

create view rackview as select r.id rackid,r.name categ,count(p.id) nop from products p,racks r where p.category=r.name group by r.id,r.name

--rack view not found

create view rackview1 as select r.id rackid,r.name categ from products p,racks r where r.name not in (select category from products) group by r.id,r.name;

-- cus message view

create view cusmsg as select sum(quantity * perunit_price) total,cusid idp,order_no ono from sales where bool=0 group by cusid,order_no having sum(quantity * perunit_price) > 50000;

----------------------------------------------------------------trigger

CREATE OR REPLACE TRIGGER pop1
BEFORE INSERT ON admin_products
FOR EACH ROW
DECLARE
  ip NUMBER;
BEGIN
  SELECT p2.id INTO ip
  FROM products p1
  JOIN racks p2 ON p1.category = p2.name
  WHERE p1.id = :new.pid;
  
  :new.rackid := ip;
  
END;

------------------------------------------------------------------
















