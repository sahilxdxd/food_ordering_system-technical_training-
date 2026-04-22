from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import date, time
from decimal import Decimal
from typing import Any, Iterable

import psycopg2
from psycopg2.extras import RealDictCursor


def db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE", "food_ordering_db"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "postgres"),
    }


@contextmanager
def get_conn():
    conn = psycopg2.connect(**db_config())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_conn_raw():
    return psycopg2.connect(**db_config())


def _exec_file(cur, path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        cur.execute(f.read())


def init_db(schema_path: str = "schema.sql") -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            _exec_file(cur, schema_path)
            _seed_if_empty(cur)


def _seed_if_empty(cur) -> None:
    def empty(table: str) -> bool:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0] == 0

    if empty("cuisine"):
        cur.executemany(
            "INSERT INTO cuisine (cuisinename) VALUES (%s)",
            [("Italian",), ("Chinese",), ("Mexican",), ("Indian",), ("Japanese",)],
        )

    if empty("employee"):
        employees = [
            ("Michael", "Johnson", date(1990, 5, 15), "mike@email.com", "emp_pass1", "789 Oak St", "5558765", "Male", 50000),
            ("Emily", "Wilson", date(1985, 2, 20), "emily@email.com", "emp_pass2", "567 Pine St", "5554321", "Female", 45000),
            ("David", "Lee", date(1988, 9, 10), "david@email.com", "emp_pass3", "654 Elm St", "5557890", "Male", 48000),
            ("Anna", "Garcia", date(1993, 3, 25), "anna@email.com", "emp_pass4", "789 Oak St", "5551234", "Female", 52000),
            ("Robert", "Brown", date(1987, 12, 12), "robert@email.com", "emp_pass5", "101 Oak St", "5553456", "Male", 55000),
        ]
        cur.executemany(
            """INSERT INTO employee
               (fname, lname, dob, emailid, pwd, address, phoneno, gender, salary)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            employees,
        )

    if empty("chef"):
        chefs = [
            ("Chef Mario", "123 Chef Way", "Apt 2C", "555-9876", 1, 1, "mario@email.com", "chef_pass1", 55000),
            ("Chef Lily", "456 Chef Lane", "Unit 5D", "555-2345", 2, 2, "lily@email.com", "chef_pass2", 52000),
            ("Chef Carlos", "789 Chef St", "Suite 1B", "555-7890", 3, 3, "carlos@email.com", "chef_pass3", 53000),
            ("Chef Priya", "101 Chef Rd", "Apt 3A", "555-4321", 4, 4, "priya@email.com", "chef_pass4", 51000),
            ("Chef Kenji", "456 Chef Ave", "Unit 4C", "555-3456", 5, 5, "kenji@email.com", "chef_pass5", 54000),
        ]
        cur.executemany(
            """INSERT INTO chef
               (chefname, address, street, phoneno, cuisineid, empid, emailid, pwd, salary)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            chefs,
        )

    if empty("ingredient"):
        cur.executemany(
            "INSERT INTO ingredient (ingname) VALUES (%s)",
            [("Tomato",), ("Chicken",), ("Beef",), ("Rice",), ("Noodles",)],
        )

    if empty("food"):
        foods = [
            ("Margherita Pizza", 12, 20, "Available", 1, 1, 1),
            ("Kung Pao Chicken", 15, 15, "Available", 2, 2, 2),
            ("Taco", 10, 30, "Available", 3, 3, 3),
            ("Chicken Biryani", 14, 25, "Available", 4, 4, 4),
            ("Sushi Rolls", 18, 20, "Available", 5, 5, 5),
        ]
        cur.executemany(
            """INSERT INTO food
               (foodname, price, quantity, foodavail, cuisineid, ingid, chefid)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            foods,
        )

    if empty("drink"):
        drinks = [
            ("Coca-Cola", 2, 40, "Available"),
            ("Sprite", 2, 35, "Available"),
            ("Lemonade", 2, 30, "Available"),
            ("Iced Tea", 2, 25, "Available"),
            ("Orange Juice", 3, 20, "Available"),
        ]
        cur.executemany(
            "INSERT INTO drink (drinkname, price, quantity, drinkavail) VALUES (%s,%s,%s,%s)",
            drinks,
        )

    if empty("delivery"):
        deliveries = [
            ("Fast Delivery", "DEL123", 5, date(2026, 4, 13), time(12, 0), None, None),
            ("Express Delivery", "DEL456", 7, date(2026, 4, 14), time(14, 30), None, None),
            ("Standard Delivery", "DEL789", 6, date(2026, 4, 15), time(15, 45), None, None),
            ("Late Night Delivery", "DEL987", 8, date(2026, 4, 16), time(21, 0), None, None),
            ("Weekend Delivery", "DEL654", 7, date(2026, 4, 17), time(10, 30), None, None),
        ]
        cur.executemany(
            """INSERT INTO delivery
               (delname, vehicleno, delcharge, deldate, deltime, custid, empid)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            deliveries,
        )

    if empty("customer"):
        customers = [
            ("professor sirji", "5551234", "123 Main St"),
            ("Yash", "5555678", "456 Elm St"),
            ("Sahil Gupta", "5559876", "789 Oak St"),
            ("arnab lala", "5554321", "567 Pine St"),
            ("Mike Brown", "5558765", "101 Oak St"),
        ]
        cur.executemany(
            "INSERT INTO customer (name, phone, address) VALUES (%s,%s,%s)",
            customers,
        )


def fetch_all(query: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    with get_conn_raw() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return list(cur.fetchall())


def execute(query: str, params: Iterable[Any] | None = None) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())


def insert_customer(name: str, phone: str, address: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO customer (name, phone, address) VALUES (%s,%s,%s) RETURNING custid",
                (name, phone, address),
            )
            return cur.fetchone()[0]


def get_menu(search: str = "") -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if search:
        like = f"%{search.lower()}%"
        foods = fetch_all(
            """SELECT foodid, foodname, price, quantity, foodavail
               FROM food
               WHERE LOWER(foodname) LIKE %s
               ORDER BY foodname""",
            (like,),
        )
        drinks = fetch_all(
            """SELECT drinkid, drinkname, price, quantity, drinkavail
               FROM drink
               WHERE LOWER(drinkname) LIKE %s
               ORDER BY drinkname""",
            (like,),
        )
    else:
        foods = fetch_all("SELECT foodid, foodname, price, quantity, foodavail FROM food ORDER BY foodname")
        drinks = fetch_all("SELECT drinkid, drinkname, price, quantity, drinkavail FROM drink ORDER BY drinkname")
    return foods, drinks


def get_customers():
    return fetch_all("SELECT custid, name, phone, address FROM customer ORDER BY custid")


def get_deliveries():
    return fetch_all("SELECT delid, delname, delcharge, vehicleno, deldate, deltime FROM delivery ORDER BY delid")


def get_orders():
    return fetch_all(
        """SELECT o.ordid, o.created_at, o.status, o.totalcost, o.paymethod,
                  c.name AS customer_name,
                  COALESCE(d.delname, '-') AS delivery_name
           FROM orders o
           JOIN customer c ON c.custid = o.custid
           LEFT JOIN delivery d ON d.delid = o.delid
           ORDER BY o.ordid DESC"""
    )


def get_order_items(order_id: int):
    return fetch_all(
        """SELECT itemid, item_type, item_name, unit_price, qty, subtotal
           FROM order_items
           WHERE ordid = %s
           ORDER BY itemid""",
        (order_id,),
    )


def get_table_rows(table_name: str):
    allowed = {
        "customer": "SELECT * FROM customer ORDER BY custid",
        "food": "SELECT * FROM food ORDER BY foodid",
        "drink": "SELECT * FROM drink ORDER BY drinkid",
        "orders": """SELECT o.*, c.name AS customer_name
                     FROM orders o JOIN customer c ON c.custid = o.custid
                     ORDER BY o.ordid DESC""",
        "payment": """SELECT p.*, c.name AS customer_name
                      FROM payment p JOIN customer c ON c.custid = p.custid
                      ORDER BY p.payid DESC""",
        "delivery": "SELECT * FROM delivery ORDER BY delid",
        "order_items": "SELECT * FROM order_items ORDER BY itemid DESC",
    }
    if table_name not in allowed:
        raise ValueError("Unsupported table.")
    return fetch_all(allowed[table_name])


def place_order(customer_id: int, delivery_id: int | None, paymethod: str, cart: list[dict[str, Any]]) -> int:
    if not cart:
        raise ValueError("Cart is empty.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            total = Decimal("0.00")
            for item in cart:
                total += Decimal(str(item["price"])) * int(item["qty"])

            cur.execute(
                "INSERT INTO orders (custid, delid, totalcost, paymethod, status) VALUES (%s,%s,%s,%s,%s) RETURNING ordid",
                (customer_id, delivery_id, total, paymethod, "Placed"),
            )
            ordid = cur.fetchone()[0]

            for item in cart:
                item_type = item["type"]
                qty = int(item["qty"])
                unit_price = Decimal(str(item["price"]))
                subtotal = unit_price * qty
                item_name = item["name"]

                if item_type == "food":
                    foodid = int(item["id"])
                    cur.execute("SELECT quantity FROM food WHERE foodid = %s FOR UPDATE", (foodid,))
                    row = cur.fetchone()
                    if row is None:
                        raise ValueError(f"Food item not found: {item_name}")
                    current = int(row[0])
                    if current < qty:
                        raise ValueError(f"Not enough stock for {item_name}. Available: {current}")
                    cur.execute("UPDATE food SET quantity = quantity - %s WHERE foodid = %s", (qty, foodid))
                    cur.execute(
                        """INSERT INTO order_items
                           (ordid, item_type, foodid, drinkid, item_name, unit_price, qty, subtotal)
                           VALUES (%s,'food',%s,NULL,%s,%s,%s,%s)""",
                        (ordid, foodid, item_name, unit_price, qty, subtotal),
                    )
                else:
                    drinkid = int(item["id"])
                    cur.execute("SELECT quantity FROM drink WHERE drinkid = %s FOR UPDATE", (drinkid,))
                    row = cur.fetchone()
                    if row is None:
                        raise ValueError(f"Drink item not found: {item_name}")
                    current = int(row[0])
                    if current < qty:
                        raise ValueError(f"Not enough stock for {item_name}. Available: {current}")
                    cur.execute("UPDATE drink SET quantity = quantity - %s WHERE drinkid = %s", (qty, drinkid))
                    cur.execute(
                        """INSERT INTO order_items
                           (ordid, item_type, foodid, drinkid, item_name, unit_price, qty, subtotal)
                           VALUES (%s,'drink',NULL,%s,%s,%s,%s,%s)""",
                        (ordid, drinkid, item_name, unit_price, qty, subtotal),
                    )

            cur.execute(
                "INSERT INTO payment (custid, ordid, paymethod, amount) VALUES (%s,%s,%s,%s)",
                (customer_id, ordid, paymethod, total),
            )

            return ordid
