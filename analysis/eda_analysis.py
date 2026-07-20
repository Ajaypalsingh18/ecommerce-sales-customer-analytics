"""
E-Commerce Sales & Customer Analytics — Exploratory Data Analysis
Loads the four CSVs, cleans them, and produces:
  - Monthly revenue trend chart
  - Category revenue breakdown
  - Top 10 products chart
  - Customer segment (RFM-lite) analysis
  - Cancellation/return rate by city
Outputs PNG charts to ../charts and a printed summary of key metrics.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["figure.dpi"] = 110
plt.style.use("seaborn-v0_8-whitegrid")

DATA_DIR = "../data"
CHART_DIR = "../charts"

# ---------- LOAD ----------
customers = pd.read_csv(f"{DATA_DIR}/customers.csv", parse_dates=["signup_date"])
products = pd.read_csv(f"{DATA_DIR}/products.csv")
orders = pd.read_csv(f"{DATA_DIR}/orders.csv", parse_dates=["order_date"])
order_items = pd.read_csv(f"{DATA_DIR}/order_items.csv")

# ---------- CLEAN ----------
# Drop exact duplicates, check nulls
for name, df in [("customers", customers), ("products", products),
                  ("orders", orders), ("order_items", order_items)]:
    before = len(df)
    df.drop_duplicates(inplace=True)
    nulls = df.isnull().sum().sum()
    print(f"{name}: {before} rows -> {len(df)} after dedup | {nulls} null values")

delivered = orders[orders["status"] == "Delivered"].copy()
delivered["order_month"] = delivered["order_date"].dt.to_period("M").astype(str)

# ---------- KEY METRICS ----------
total_revenue = delivered["order_total"].sum()
total_orders = len(delivered)
aov = delivered["order_total"].mean()
cancel_return_rate = (orders["status"].isin(["Cancelled", "Returned"]).sum() / len(orders)) * 100

print("\n===== KEY METRICS =====")
print(f"Total Revenue (Delivered): Rs {total_revenue:,.0f}")
print(f"Total Delivered Orders: {total_orders:,}")
print(f"Average Order Value: Rs {aov:,.0f}")
print(f"Cancellation/Return Rate: {cancel_return_rate:.1f}%")

# ---------- CHART 1: Monthly Revenue Trend ----------
monthly = delivered.groupby("order_month")["order_total"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["order_month"], monthly["order_total"], marker="o", linewidth=2, color="#2563eb")
ax.fill_between(range(len(monthly)), monthly["order_total"], alpha=0.1, color="#2563eb")
ax.set_title("Monthly Revenue Trend (Jan 2025 – Mar 2026)", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue (Rs )")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs {x/1e5:.1f}L"))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_monthly_revenue_trend.png")
plt.close()

# ---------- CHART 2: Revenue by Category ----------
items_joined = order_items.merge(products, on="product_id").merge(
    orders[orders["status"] == "Delivered"][["order_id"]], on="order_id")
cat_revenue = items_joined.groupby("category")["line_total"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(cat_revenue.index, cat_revenue.values, color="#2563eb")
ax.set_title("Revenue by Product Category", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue (Rs )")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs {x/1e5:.1f}L"))
for bar in bars:
    w = bar.get_width()
    ax.text(w, bar.get_y() + bar.get_height()/2, f" Rs {w/1e5:.1f}L", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_revenue_by_category.png")
plt.close()

# ---------- CHART 3: Top 10 Products ----------
top_products = items_joined.groupby("product_name")["line_total"].sum().nlargest(10).sort_values()
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(top_products.index, top_products.values, color="#16a34a")
ax.set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue (Rs )")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs {x/1e3:.0f}K"))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_top10_products.png")
plt.close()

# ---------- CHART 4: Customer Segment Revenue Share ----------
cust_rev = delivered.merge(customers, on="customer_id").groupby("segment")["order_total"].sum()
fig, ax = plt.subplots(figsize=(6, 6))
colors = ["#93c5fd", "#2563eb", "#1e3a8a"]
wedges, texts, autotexts = ax.pie(
    cust_rev.values, labels=cust_rev.index, autopct="%1.1f%%",
    colors=colors, startangle=90, textprops={"fontsize": 10}
)
ax.set_title("Revenue Share by Customer Segment", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_segment_revenue_share.png")
plt.close()

# ---------- CHART 5: Cancellation/Return Rate by City ----------
city_stats = orders.merge(customers, on="customer_id").groupby("city").agg(
    total=("order_id", "count"),
    bad=("status", lambda s: s.isin(["Cancelled", "Returned"]).sum())
)
city_stats["rate"] = (city_stats["bad"] / city_stats["total"] * 100).round(1)
city_stats = city_stats.sort_values("rate", ascending=True)
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(city_stats.index, city_stats["rate"], color="#dc2626")
ax.set_title("Cancellation / Return Rate by City", fontsize=13, fontweight="bold")
ax.set_xlabel("Rate (%)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_cancel_return_by_city.png")
plt.close()

# ---------- Pareto: top 20% customers ----------
cust_ltv = delivered.groupby("customer_id")["order_total"].sum().sort_values(ascending=False)
top20_cutoff = int(len(cust_ltv) * 0.2)
top20_share = cust_ltv.iloc[:top20_cutoff].sum() / cust_ltv.sum() * 100
print(f"Top 20% of customers drive {top20_share:.1f}% of revenue")

# Repeat purchase rate
order_counts = delivered.groupby("customer_id").size()
repeat_rate = (order_counts >= 2).sum() / len(order_counts) * 100
print(f"Repeat purchase rate: {repeat_rate:.1f}%")

print("\nCharts saved to ../charts/")
