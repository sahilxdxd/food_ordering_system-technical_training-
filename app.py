from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from decimal import Decimal
from typing import Any

import pandas as pd

import db


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Food Ordering System")
        self.root.geometry("1280x760")
        self.root.minsize(1150, 700)

        self.cart: list[dict[str, Any]] = []
        self.current_search = tk.StringVar()
        self.total_var = tk.StringVar(value="Total: Rs 0.00")
        self.status_var = tk.StringVar(value="Ready")

        self._setup_style()
        self._build_ui()
        self.refresh_all()

    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        bg = "#f5f7fb"
        panel = "#ffffff"
        text = "#1f2937"

        self.root.configure(bg=bg)
        style.configure("TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel)
        style.configure("TLabel", background=bg, foreground=text, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=bg, foreground=text, font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabel", background=bg, foreground=text, font=("Segoe UI", 12, "bold"))
        style.configure("Hint.TLabel", background=bg, foreground="#6b7280", font=("Segoe UI", 9, "italic"))
        style.configure("TButton", padding=7, font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#dbeafe")])

    def _build_ui(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=14, pady=(12, 8))

        ttk.Label(header, text="Food Ordering System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="PostgreSQL-backed DBMS project with modular code, cart checkout, and admin views.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        topbar = ttk.Frame(self.root)
        topbar.pack(fill="x", padx=14, pady=(0, 8))

        ttk.Label(topbar, text="Search menu:").pack(side="left")
        search_entry = ttk.Entry(topbar, textvariable=self.current_search, width=30)
        search_entry.pack(side="left", padx=(8, 6))
        search_entry.bind("<Return>", lambda e: self.refresh_menu())

        ttk.Button(topbar, text="Search", command=self.refresh_menu).pack(side="left", padx=4)
        ttk.Button(topbar, text="Clear", command=self.clear_search).pack(side="left", padx=4)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=8)

        self.menu_tab = ttk.Frame(self.notebook)
        self.cart_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.orders_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.menu_tab, text="Menu")
        self.notebook.add(self.cart_tab, text="Cart")
        self.notebook.add(self.orders_tab, text="Orders")
        self.notebook.add(self.admin_tab, text="Admin")

        self._build_menu_tab()
        self._build_cart_tab()
        self._build_orders_tab()
        self._build_admin_tab()

        status = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

    def _build_menu_tab(self):
        container = ttk.Frame(self.menu_tab)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(container)
        right = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        ttk.Label(left, text="Food Items", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.food_tree = self._build_tree(left, ("ID", "Name", "Price", "Qty", "Status"), widths=(70, 290, 90, 80, 100))
        self.food_tree.bind("<Double-1>", lambda e: self.add_selected_to_cart("food"))

        ttk.Label(right, text="Drinks", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.drink_tree = self._build_tree(right, ("ID", "Name", "Price", "Qty", "Status"), widths=(70, 290, 90, 80, 100))
        self.drink_tree.bind("<Double-1>", lambda e: self.add_selected_to_cart("drink"))

        footer = ttk.Frame(self.menu_tab)
        footer.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(footer, text="Refresh Menu", command=self.refresh_menu).pack(side="left")
        ttk.Button(footer, text="Add Selected to Cart", command=lambda: self.add_selected_to_cart()).pack(side="left", padx=8)
        ttk.Label(footer, text="Double-click an item to add it to the cart.", style="Hint.TLabel").pack(side="left", padx=10)

    def _build_cart_tab(self):
        wrapper = ttk.Frame(self.cart_tab)
        wrapper.pack(fill="both", expand=True, padx=8, pady=8)

        top = ttk.Frame(wrapper)
        top.pack(fill="both", expand=True)

        self.cart_tree = self._build_tree(
            top,
            ("Type", "Name", "Unit Price", "Qty", "Subtotal"),
            widths=(90, 310, 110, 80, 110),
        )

        controls = ttk.Frame(wrapper)
        controls.pack(fill="x", pady=8)
        ttk.Button(controls, text="Remove Selected", command=self.remove_selected_cart).pack(side="left")
        ttk.Button(controls, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=6)
        ttk.Button(controls, text="Checkout", command=self.checkout).pack(side="right")

        summary = ttk.Frame(wrapper)
        summary.pack(fill="x")
        ttk.Label(summary, textvariable=self.total_var, style="Section.TLabel").pack(anchor="e")

    def _build_orders_tab(self):
        wrapper = ttk.Frame(self.orders_tab)
        wrapper.pack(fill="both", expand=True, padx=8, pady=8)

        self.orders_tree = self._build_tree(
            wrapper,
            ("Order ID", "Customer", "Delivery", "Total", "Payment", "Status", "Created"),
            widths=(90, 180, 160, 100, 100, 100, 180),
        )

        controls = ttk.Frame(wrapper)
        controls.pack(fill="x", pady=8)
        ttk.Button(controls, text="Refresh Orders", command=self.refresh_orders).pack(side="left")
        ttk.Button(controls, text="View Items", command=self.view_selected_order_items).pack(side="left", padx=6)

    def _build_admin_tab(self):
        wrapper = ttk.Frame(self.admin_tab)
        wrapper.pack(fill="both", expand=True, padx=8, pady=8)

        buttons = ttk.Frame(wrapper)
        buttons.pack(fill="x", pady=(0, 8))

        for text, table in [
            ("Customers", "customer"),
            ("Food", "food"),
            ("Drink", "drink"),
            ("Delivery", "delivery"),
            ("Orders", "orders"),
            ("Payments", "payment"),
            ("Order Items", "order_items"),
        ]:
            ttk.Button(buttons, text=text, command=lambda t=table: self.show_table(t)).pack(side="left", padx=3)

        ttk.Button(buttons, text="Add Customer", command=self.add_customer_dialog).pack(side="right", padx=3)
        ttk.Button(buttons, text="Add Food", command=self.add_food_dialog).pack(side="right", padx=3)

        self.admin_info = ttk.Label(wrapper, text="Select a table to inspect records.", style="Hint.TLabel")
        self.admin_info.pack(anchor="w", pady=(0, 6))

        self.admin_frame = ttk.Frame(wrapper)
        self.admin_frame.pack(fill="both", expand=True)

    def _build_tree(self, parent, headings, widths):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=headings, show="headings")
        for head, width in zip(headings, widths):
            tree.heading(head, text=head)
            tree.column(head, width=width, anchor="center" if head in {"ID", "Price", "Qty", "Type", "Total", "Payment"} else "w")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def refresh_all(self):
        self.refresh_menu()
        self.refresh_cart()
        self.refresh_orders()
        self.status_var.set("Database loaded successfully.")

    def clear_search(self):
        self.current_search.set("")
        self.refresh_menu()

    def refresh_menu(self):
        search = self.current_search.get().strip()
        foods, drinks = db.get_menu(search)

        for tree in (self.food_tree, self.drink_tree):
            for item in tree.get_children():
                tree.delete(item)

        for idx, row in enumerate(foods, start=1):
            tag = "even" if idx % 2 == 0 else "odd"
            self.food_tree.insert(
                "",
                "end",
                iid=f"food_{row['foodid']}",
                values=(row["foodid"], row["foodname"], f"Rs {row['price']}", row["quantity"], row["foodavail"]),
                tags=(tag,),
            )

        for idx, row in enumerate(drinks, start=1):
            tag = "even" if idx % 2 == 0 else "odd"
            self.drink_tree.insert(
                "",
                "end",
                iid=f"drink_{row['drinkid']}",
                values=(row["drinkid"], row["drinkname"], f"Rs {row['price']}", row["quantity"], row["drinkavail"]),
                tags=(tag,),
            )

        for tree in (self.food_tree, self.drink_tree):
            tree.tag_configure("odd", background="#ffffff")
            tree.tag_configure("even", background="#f8fafc")

        self.status_var.set(f"Menu refreshed{' with search: ' + search if search else ''}.")

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = Decimal("0.00")
        for idx, item in enumerate(self.cart, start=1):
            subtotal = Decimal(str(item["price"])) * int(item["qty"])
            total += subtotal
            self.cart_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(item["type"].title(), item["name"], f"Rs {item['price']}", item["qty"], f"Rs {subtotal:.2f}"),
            )

        self.total_var.set(f"Total: Rs {total:.2f}")

    def refresh_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        try:
            orders = db.get_orders()
            for row in orders:
                self.orders_tree.insert(
                    "",
                    "end",
                    iid=str(row["ordid"]),
                    values=(
                        row["ordid"],
                        row["customer_name"],
                        row["delivery_name"],
                        f"Rs {row['totalcost']}",
                        row["paymethod"],
                        row["status"],
                        row["created_at"].strftime("%Y-%m-%d %H:%M") if row["created_at"] else "",
                    ),
                )
        except Exception as exc:
            self.status_var.set(f"Could not load orders: {exc}")

    def get_selected_row(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        return tree.item(sel[0], "values")

    def add_selected_to_cart(self, kind: str | None = None):
        source = None
        if kind == "food":
            source = self.food_tree
        elif kind == "drink":
            source = self.drink_tree
        else:
            source = self.food_tree if self.notebook.index(self.notebook.select()) == 0 else self.drink_tree

        row = self.get_selected_row(source)
        if not row:
            messagebox.showwarning("Select item", "Please select an item first.")
            return

        item_id = int(row[0])
        name = row[1]
        qty_available = int(row[3])
        price = float(str(row[2]).replace("Rs", "").strip())

        qty = simpledialog.askinteger(
            "Quantity",
            f"How many of {name}?",
            minvalue=1,
            maxvalue=max(1, qty_available),
        )
        if not qty:
            return

        item_type = "food" if source == self.food_tree else "drink"
        self.cart.append({"type": item_type, "id": item_id, "name": name, "price": price, "qty": qty})
        self.refresh_cart()
        self.status_var.set(f"Added {qty} x {name} to cart.")

    def remove_selected_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = int(sel[0]) - 1
        if 0 <= idx < len(self.cart):
            removed = self.cart.pop(idx)
            self.refresh_cart()
            self.status_var.set(f"Removed {removed['name']} from cart.")

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart()
        self.status_var.set("Cart cleared.")

    def add_customer_dialog(self):
        top = tk.Toplevel(self.root)
        top.title("Add Customer")
        top.geometry("420x220")
        top.transient(self.root)
        top.grab_set()

        fields = {}
        for i, label in enumerate(["Name", "Phone", "Address"]):
            ttk.Label(top, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=8)
            entry = ttk.Entry(top, width=40)
            entry.grid(row=i, column=1, padx=10, pady=8)
            fields[label.lower()] = entry

        def save():
            name = fields["name"].get().strip()
            phone = fields["phone"].get().strip()
            address = fields["address"].get().strip()
            if not name:
                messagebox.showerror("Validation", "Customer name is required.", parent=top)
                return
            custid = db.insert_customer(name, phone, address)
            messagebox.showinfo("Saved", f"Customer added successfully.\nCustomer ID: {custid}", parent=top)
            top.destroy()

        ttk.Button(top, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=18)

    def add_food_dialog(self):
        top = tk.Toplevel(self.root)
        top.title("Add Food")
        top.geometry("440x360")
        top.transient(self.root)
        top.grab_set()

        labels = [
            ("Food Name", "foodname"),
            ("Price", "price"),
            ("Quantity", "quantity"),
            ("Availability", "foodavail"),
            ("Cuisine ID", "cuisineid"),
            ("Ingredient ID", "ingid"),
            ("Chef ID", "chefid"),
        ]
        entries: dict[str, ttk.Entry] = {}

        for i, (label, key) in enumerate(labels):
            ttk.Label(top, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=7)
            entry = ttk.Entry(top, width=30)
            entry.grid(row=i, column=1, padx=10, pady=7)
            entries[key] = entry

        def save():
            try:
                with db.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO food
                               (foodname, price, quantity, foodavail, cuisineid, ingid, chefid)
                               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                            (
                                entries["foodname"].get().strip(),
                                Decimal(entries["price"].get().strip()),
                                int(entries["quantity"].get().strip()),
                                entries["foodavail"].get().strip() or "Available",
                                int(entries["cuisineid"].get().strip()) if entries["cuisineid"].get().strip() else None,
                                int(entries["ingid"].get().strip()) if entries["ingid"].get().strip() else None,
                                int(entries["chefid"].get().strip()) if entries["chefid"].get().strip() else None,
                            ),
                        )
                messagebox.showinfo("Saved", "Food item added successfully.", parent=top)
                top.destroy()
                self.refresh_menu()
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=top)

        ttk.Button(top, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=18)

    def show_table(self, table_name: str):
        for child in self.admin_frame.winfo_children():
            child.destroy()

        try:
            rows = db.get_table_rows(table_name)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        if not rows:
            ttk.Label(self.admin_frame, text="No records found.", style="Hint.TLabel").pack(anchor="w")
            return

        df = pd.DataFrame(rows)
        columns = list(df.columns)
        tree = ttk.Treeview(self.admin_frame, columns=columns, show="headings")
        tree.pack(fill="both", expand=True, side="left")

        vsb = ttk.Scrollbar(self.admin_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=max(110, min(180, 14 * len(col))), anchor="w")

        for _, row in df.iterrows():
            values = []
            for val in row.tolist():
                if hasattr(val, "strftime"):
                    values.append(val.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    values.append(val)
            tree.insert("", "end", values=values)

        self.admin_info.configure(text=f"Showing table: {table_name}")

    def view_selected_order_items(self):
        row = self.get_selected_row(self.orders_tree)
        if not row:
            messagebox.showwarning("Select order", "Select an order first.")
            return
        order_id = int(row[0])
        items = db.get_order_items(order_id)
        if not items:
            messagebox.showinfo("Order items", "No items found for this order.")
            return

        top = tk.Toplevel(self.root)
        top.title(f"Order Items - #{order_id}")
        top.geometry("760x360")
        top.transient(self.root)

        tree = self._build_tree(top, ("ID", "Type", "Item", "Unit Price", "Qty", "Subtotal"), widths=(70, 90, 260, 110, 80, 110))
        for item in items:
            tree.insert(
                "",
                "end",
                values=(
                    item["itemid"],
                    item["item_type"].title(),
                    item["item_name"],
                    f"Rs {item['unit_price']}",
                    item["qty"],
                    f"Rs {item['subtotal']}",
                ),
            )

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty cart", "Add items to the cart first.")
            return

        customers = db.get_customers()
        if not customers:
            messagebox.showerror("No customer", "No customers found. Add a customer first.")
            return

        cust_window = tk.Toplevel(self.root)
        cust_window.title("Checkout")
        cust_window.geometry("460x320")
        cust_window.transient(self.root)
        cust_window.grab_set()

        ttk.Label(cust_window, text="Select Customer").pack(anchor="w", padx=12, pady=(12, 4))
        customer_map = {f"{c['custid']} - {c['name']}": c["custid"] for c in customers}
        customer_combo = ttk.Combobox(cust_window, values=list(customer_map.keys()), state="readonly", width=50)
        customer_combo.pack(padx=12, pady=4)
        customer_combo.current(0)

        ttk.Label(cust_window, text="Select Delivery").pack(anchor="w", padx=12, pady=(12, 4))
        deliveries = db.get_deliveries()
        delivery_values = ["None"]
        delivery_map = {"None": None}
        for d in deliveries:
            label = f"{d['delid']} - {d['delname']} (Rs {d['delcharge']})"
            delivery_values.append(label)
            delivery_map[label] = d["delid"]
        delivery_combo = ttk.Combobox(cust_window, values=delivery_values, state="readonly", width=50)
        delivery_combo.pack(padx=12, pady=4)
        delivery_combo.current(0)

        ttk.Label(cust_window, text="Payment Method").pack(anchor="w", padx=12, pady=(12, 4))
        pay_combo = ttk.Combobox(cust_window, values=["Cash", "Card", "UPI", "Net Banking"], state="readonly", width=50)
        pay_combo.pack(padx=12, pady=4)
        pay_combo.current(0)

        def finalize():
            try:
                cust_key = customer_combo.get()
                if not cust_key:
                    raise ValueError("Select a customer.")
                customer_id = customer_map[cust_key]
                delivery_id = delivery_map.get(delivery_combo.get())
                paymethod = pay_combo.get() or "Cash"

                ordid = db.place_order(customer_id, delivery_id, paymethod, self.cart)
                self.cart.clear()
                self.refresh_cart()
                self.refresh_menu()
                self.refresh_orders()
                messagebox.showinfo("Success", f"Order #{ordid} placed successfully.", parent=cust_window)
                cust_window.destroy()
            except Exception as exc:
                messagebox.showerror("Checkout failed", str(exc), parent=cust_window)

        ttk.Button(cust_window, text="Place Order", command=finalize).pack(pady=18)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    db.init_db("schema.sql")
    root = tk.Tk()
    App(root).run()
