import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# SQL Server details
server = r"BLINDXDHAKAD\SQLEXPRESS"
database = "ShopPulse"

# Windows Authentication + ODBC Driver 18
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(
    "mssql+pyodbc:///?odbc_connect=" + quote_plus(connection_string)
)

print("Connected to SQL Server!")

# -----------------------------
# 1. Customers
# -----------------------------
customers = pd.read_csv("data/olist_customers_dataset.csv")

customers.to_sql(
    "customers",
    engine,
    if_exists="append",
    index=False
)

print(f"Customers loaded: {len(customers)}")


# -----------------------------
# 2. Orders
# -----------------------------
orders = pd.read_csv("data/olist_orders_dataset.csv")

orders.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False
)

print(f"Orders loaded: {len(orders)}")


# -----------------------------
# 3. Order Items
# -----------------------------
order_items = pd.read_csv("data/olist_order_items_dataset.csv")

order_items.to_sql(
    "order_items",
    engine,
    if_exists="append",
    index=False
)

print(f"Order items loaded: {len(order_items)}")


# -----------------------------
# 4. Website Events
# -----------------------------
events = pd.read_csv("data/website_events.csv")

events.to_sql(
    "website_events",
    engine,
    if_exists="append",
    index=False
)

print(f"Website events loaded: {len(events)}")


# -----------------------------
# 5. A/B Test Assignments
# -----------------------------
assignments = pd.read_csv("data/ab_test_assignments.csv")

assignments.to_sql(
    "ab_test_assignments",
    engine,
    if_exists="append",
    index=False
)

print(f"A/B assignments loaded: {len(assignments)}")

print("\nALL DATA LOADED SUCCESSFULLY!")