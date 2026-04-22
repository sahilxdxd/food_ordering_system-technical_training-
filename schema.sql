-- PostgreSQL schema for Food Ordering App

CREATE TABLE IF NOT EXISTS customer (
    custid SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    address TEXT
);

CREATE TABLE IF NOT EXISTS cuisine (
    cuisineid SERIAL PRIMARY KEY,
    cuisinename VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS employee (
    empid SERIAL PRIMARY KEY,
    fname VARCHAR(60) NOT NULL,
    lname VARCHAR(60) NOT NULL,
    dob DATE,
    emailid VARCHAR(120) UNIQUE,
    pwd VARCHAR(120),
    address TEXT,
    phoneno VARCHAR(20),
    gender VARCHAR(20),
    salary NUMERIC(12,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chef (
    chefid SERIAL PRIMARY KEY,
    chefname VARCHAR(120) NOT NULL,
    address TEXT,
    street TEXT,
    phoneno VARCHAR(20),
    cuisineid INTEGER REFERENCES cuisine(cuisineid) ON DELETE SET NULL,
    empid INTEGER REFERENCES employee(empid) ON DELETE SET NULL,
    emailid VARCHAR(120) UNIQUE,
    pwd VARCHAR(120),
    salary NUMERIC(12,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ingredient (
    ingid SERIAL PRIMARY KEY,
    ingname VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS food (
    foodid SERIAL PRIMARY KEY,
    foodname VARCHAR(120) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    foodavail VARCHAR(20) NOT NULL DEFAULT 'Available',
    cuisineid INTEGER REFERENCES cuisine(cuisineid) ON DELETE SET NULL,
    ingid INTEGER REFERENCES ingredient(ingid) ON DELETE SET NULL,
    chefid INTEGER REFERENCES chef(chefid) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS drink (
    drinkid SERIAL PRIMARY KEY,
    drinkname VARCHAR(120) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    drinkavail VARCHAR(20) NOT NULL DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS delivery (
    delid SERIAL PRIMARY KEY,
    delname VARCHAR(120) NOT NULL,
    vehicleno VARCHAR(40),
    delcharge NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (delcharge >= 0),
    deldate DATE,
    deltime TIME,
    custid INTEGER REFERENCES customer(custid) ON DELETE SET NULL,
    empid INTEGER REFERENCES employee(empid) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS orders (
    ordid SERIAL PRIMARY KEY,
    custid INTEGER NOT NULL REFERENCES customer(custid) ON DELETE RESTRICT,
    delid INTEGER REFERENCES delivery(delid) ON DELETE SET NULL,
    totalcost NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (totalcost >= 0),
    paymethod VARCHAR(40) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Placed',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    itemid SERIAL PRIMARY KEY,
    ordid INTEGER NOT NULL REFERENCES orders(ordid) ON DELETE CASCADE,
    item_type VARCHAR(10) NOT NULL CHECK (item_type IN ('food', 'drink')),
    foodid INTEGER REFERENCES food(foodid) ON DELETE RESTRICT,
    drinkid INTEGER REFERENCES drink(drinkid) ON DELETE RESTRICT,
    item_name VARCHAR(120) NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    qty INTEGER NOT NULL CHECK (qty > 0),
    subtotal NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT order_item_type_check CHECK (
        (item_type = 'food' AND foodid IS NOT NULL AND drinkid IS NULL)
        OR
        (item_type = 'drink' AND drinkid IS NOT NULL AND foodid IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS payment (
    payid SERIAL PRIMARY KEY,
    custid INTEGER NOT NULL REFERENCES customer(custid) ON DELETE RESTRICT,
    ordid INTEGER NOT NULL REFERENCES orders(ordid) ON DELETE CASCADE,
    paymethod VARCHAR(40) NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    paid_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_food_name ON food (foodname);
CREATE INDEX IF NOT EXISTS idx_drink_name ON drink (drinkname);
CREATE INDEX IF NOT EXISTS idx_order_customer ON orders (custid);
CREATE INDEX IF NOT EXISTS idx_order_created ON orders (created_at);
