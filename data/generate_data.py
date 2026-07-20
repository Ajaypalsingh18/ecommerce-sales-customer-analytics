"""
Generates a realistic synthetic e-commerce dataset:
customers.csv, products.csv, orders.csv

Simulates 15 months of order history (Jan 2025 - Mar 2026) for an
Indian e-commerce retailer, including seasonality, repeat customers,
and a small % of cancelled/returned orders.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------- CUSTOMERS ----------
FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna","Ishaan","Rohan",
               "Ananya","Diya","Isha","Kavya","Myra","Aadhya","Saanvi","Anika","Riya","Priya",
               "Rahul","Amit","Neha","Pooja","Sanjay","Deepak","Meera","Kiran","Vikram","Nisha"]
LAST_NAMES = ["Sharma","Verma","Gupta","Singh","Kumar","Patel","Reddy","Nair","Iyer","Mehta",
              "Joshi","Chopra","Malhotra","Kapoor","Bhatia","Rao","Pillai","Das","Sinha","Agarwal"]
CITIES = [("Delhi","North"),("Mumbai","West"),("Bengaluru","South"),("Hyderabad","South"),
          ("Chennai","South"),("Pune","West"),("Kolkata","East"),("Ahmedabad","West"),
          ("Jaipur","North"),("Lucknow","North"),("Chandigarh","North"),("Nagpur","West")]

N_CUSTOMERS = 1200
customers = []
signup_start = datetime(2024, 1, 1)
for i in range(1, N_CUSTOMERS + 1):
    fn, ln = np.random.choice(FIRST_NAMES), np.random.choice(LAST_NAMES)
    city, region = CITIES[np.random.randint(len(CITIES))]
    signup_date = signup_start + timedelta(days=int(np.random.randint(0, 450)))
    segment = np.random.choice(["New","Regular","Premium"], p=[0.45, 0.40, 0.15])
    customers.append({
        "customer_id": f"CUST{i:05d}",
        "first_name": fn, "last_name": ln,
        "city": city, "region": region,
        "signup_date": signup_date.strftime("%Y-%m-%d"),
        "segment": segment
    })
customers_df = pd.DataFrame(customers)

# ---------- PRODUCTS ----------
CATALOG = {
    "Electronics": ["Wireless Earbuds","Bluetooth Speaker","Smartwatch","Power Bank 20000mAh",
                    "USB-C Charger","Laptop Backpack","Wireless Mouse","Mechanical Keyboard"],
    "Fashion": ["Cotton T-Shirt","Denim Jeans","Running Shoes","Leather Wallet","Sunglasses",
                "Formal Shirt","Sports Cap","Backpack"],
    "Home & Kitchen": ["Non-Stick Pan Set","Electric Kettle","LED Desk Lamp","Storage Containers",
                       "Bedsheet Set","Air Fryer","Vacuum Flask"],
    "Beauty": ["Face Wash","Moisturizer","Sunscreen SPF50","Hair Serum","Lipstick","Perfume"],
    "Sports & Fitness": ["Yoga Mat","Resistance Bands","Dumbbell Set","Skipping Rope","Gym Bag"],
    "Books & Stationery": ["Notebook Set","Fountain Pen","Desk Organizer","Sticky Notes Pack"]
}
PRICE_RANGES = {
    "Electronics": (699, 4999), "Fashion": (299, 2499), "Home & Kitchen": (399, 3499),
    "Beauty": (149, 1299), "Sports & Fitness": (249, 2999), "Books & Stationery": (49, 599)
}

products = []
pid = 1
for cat, items in CATALOG.items():
    lo, hi = PRICE_RANGES[cat]
    for item in items:
        price = int(np.random.randint(lo, hi) // 10 * 10 - 1)  # X99 style pricing
        cost_ratio = np.random.uniform(0.55, 0.72)
        products.append({
            "product_id": f"PROD{pid:04d}",
            "product_name": item,
            "category": cat,
            "unit_price": max(price, 49),
            "unit_cost": round(max(price, 49) * cost_ratio, 2)
        })
        pid += 1
products_df = pd.DataFrame(products)

# ---------- ORDERS ----------
START = datetime(2025, 1, 1)
END = datetime(2026, 3, 31)
n_days = (END - START).days

# Monthly seasonality multiplier (festive/sale months higher: Oct-Nov, Jan, Jul)
MONTH_WEIGHT = {1:1.3, 2:0.9, 3:0.95, 4:0.85, 5:0.9, 6:0.95, 7:1.15, 8:0.95,
                 9:1.0, 10:1.5, 11:1.6, 12:1.2}

customer_ids = customers_df["customer_id"].values
customer_weights = np.where(customers_df["segment"] == "Premium", 3.0,
                    np.where(customers_df["segment"] == "Regular", 1.6, 1.0))
customer_weights = customer_weights / customer_weights.sum()

STATUSES = ["Delivered","Delivered","Delivered","Delivered","Delivered",
            "Delivered","Delivered","Cancelled","Returned"]
PAYMENT = ["UPI","Credit Card","Debit Card","Cash on Delivery","Net Banking"]

orders = []
order_items = []
order_id = 1
item_id = 1

for day_offset in range(n_days):
    day = START + timedelta(days=day_offset)
    weight = MONTH_WEIGHT[day.month]
    weekend_boost = 1.25 if day.weekday() >= 5 else 1.0
    base_orders = np.random.poisson(lam=14 * weight * weekend_boost)

    for _ in range(base_orders):
        cust = np.random.choice(customer_ids, p=customer_weights)
        n_items = np.random.choice([1, 1, 2, 2, 3, 4], p=[0.35, 0.25, 0.2, 0.1, 0.07, 0.03])
        chosen_products = products_df.sample(n=n_items, replace=False)
        status = np.random.choice(STATUSES)
        order_total = 0
        for _, prod in chosen_products.iterrows():
            qty = np.random.choice([1, 1, 1, 2, 3], p=[0.55, 0.2, 0.1, 0.1, 0.05])
            line_total = round(prod["unit_price"] * qty, 2)
            order_total += line_total
            order_items.append({
                "order_item_id": f"OI{item_id:06d}",
                "order_id": f"ORD{order_id:06d}",
                "product_id": prod["product_id"],
                "quantity": int(qty),
                "unit_price": prod["unit_price"],
                "line_total": line_total
            })
            item_id += 1

        orders.append({
            "order_id": f"ORD{order_id:06d}",
            "customer_id": cust,
            "order_date": day.strftime("%Y-%m-%d"),
            "status": status,
            "payment_method": np.random.choice(PAYMENT),
            "order_total": round(order_total, 2)
        })
        order_id += 1

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)

customers_df.to_csv("customers.csv", index=False)
products_df.to_csv("products.csv", index=False)
orders_df.to_csv("orders.csv", index=False)
order_items_df.to_csv("order_items.csv", index=False)

print(f"Customers: {len(customers_df)}")
print(f"Products: {len(products_df)}")
print(f"Orders: {len(orders_df)}")
print(f"Order items: {len(order_items_df)}")
print(f"Date range: {orders_df['order_date'].min()} to {orders_df['order_date'].max()}")
