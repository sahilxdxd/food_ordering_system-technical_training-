# Food Ordering System (PostgreSQL + Tkinter)

A modular DBMS project for MCA-level submission.

## Project Structure

- `app.py` — Tkinter GUI
- `db.py` — PostgreSQL connection, seeding, and CRUD helpers
- `schema.sql` — PostgreSQL schema
- `requirements.txt` — Python dependencies

## Main Improvements

- Migrated from SQLite to PostgreSQL
- Split the project into separate files
- Normalized order flow with `orders` and `order_items`
- Added transaction-safe checkout
- Added search bar, cart cleanup, order viewer, and admin panels
- Added live quantity updates for both food and drinks

## Requirements

- Python 3.10+
- PostgreSQL 13+ recommended
- `pip`

## Create the database

Open PostgreSQL and create a database:

```sql
CREATE DATABASE food_ordering_db;
```

Then use the same name in your environment variables or keep the default.

## Install dependencies

```bash
pip install -r requirements.txt
```

## Set PostgreSQL credentials

### Windows PowerShell
```powershell
$env:PGHOST="localhost"
$env:PGPORT="5432"
$env:PGDATABASE="food_ordering_db"
$env:PGUSER="postgres"
$env:PGPASSWORD="your_password"
```

### Linux / macOS
```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=food_ordering_db
export PGUSER=postgres
export PGPASSWORD=your_password
```

## Run

```bash
python app.py
```

On first run, the app will:
1. Create the tables if they do not exist
2. Insert sample data if the tables are empty
3. Open the GUI

## Notes

- Do not use `foodid` manually while adding food; PostgreSQL generates it automatically.
- Checkout is transaction-safe.
- Every order stores each item separately in `order_items`.

## Suggested submission points

- DBMS concepts shown: normalization, foreign keys, transaction handling, and query-based admin views
- GUI concepts shown: Tkinter, Treeview tables, checkout flow, and live cart management
- PostgreSQL concepts shown: serial keys, constraints, cascading relations, indexes
