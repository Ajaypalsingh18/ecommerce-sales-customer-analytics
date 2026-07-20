# 📊 E-Commerce Sales & Customer Analytics

End-to-end data analysis project simulating a real e-commerce retailer's sales, customer, and product data — covering data cleaning, SQL analysis, exploratory data analysis (EDA), and business insights.

## 🎯 Business Problem
An e-commerce retailer wants to understand: Which products/categories drive revenue? Who are the most valuable customers? Where are order cancellations hurting the business? This project answers those questions using SQL and Python, the same way a data analyst would approach a real stakeholder request.

## 🗂️ Dataset
Synthetic but realistic dataset generated to mirror real e-commerce transaction patterns (seasonality, repeat customers, regional spread across India, cancellations/returns):

| Table | Rows | Description |
|---|---|---|
| `customers.csv` | 1,200 | Customer demographics, city, region, signup date, segment |
| `products.csv` | 38 | Product catalog across 6 categories |
| `orders.csv` | 7,460 | Order-level data: date, status, payment method, total |
| `order_items.csv` | 11,493 | Line-item detail per order |

Data spans **Jan 2025 – Mar 2026** (15 months), built with realistic seasonality (festive-season spikes in Oct–Nov, weekend order boosts) and a customer segment mix (New/Regular/Premium) that drives repeat-purchase behavior.

## 🔑 Key Insights

| Metric | Value |
|---|---|
| Total Revenue (Delivered orders) | ₹18,521,008 (₹1.85 Cr) |
| Total Delivered Orders | 5,849 |
| Average Order Value | ₹3,167 |
| Cancellation/Return Rate | 21.6% |
| **Top 20% of customers drive** | **43.4% of total revenue** |
| Repeat Purchase Rate | 92.1% of customers ordered 2+ times |
| Top Category | Electronics (highest revenue share) |
| Highest cancellation/return city | Mumbai (23.8%) — flagged for logistics review |

**So what?** The 43.4% revenue concentration in the top quintile of customers means a loyalty/retention program targeting Premium-segment customers would protect a disproportionate share of revenue. The 21.6% cancellation rate is high enough to warrant a root-cause investigation by city and payment method — both broken out in the SQL queries.

## 📈 Charts
All charts in [`/charts`](./charts):
1. Monthly revenue trend (seasonality visible around Oct–Nov)
2. Revenue by product category
3. Top 10 products by revenue
4. Revenue share by customer segment
5. Cancellation/return rate by city

## 🗃️ SQL Analysis
[`sql/analysis_queries.sql`](./sql/analysis_queries.sql) — 10 queries covering:
- Joins across 4 tables
- CTEs (Customer Lifetime Value, repeat-purchase rate)
- Window functions (`RANK`, `NTILE`, `LAG` for month-over-month growth)
- Subqueries (Pareto/80-20 revenue concentration check)

Run it yourself:
```bash
cd data
python3 generate_data.py             # builds the CSVs
python3 build_db.py                  # loads CSVs into SQLite (ecommerce.db)
cd ..
sqlite3 data/ecommerce.db < sql/analysis_queries.sql
```

## 🐍 Python EDA
[`analysis/eda_analysis.py`](./analysis/eda_analysis.py) — pandas-based cleaning (dedup + null checks), aggregation, and matplotlib visualization.
```bash
cd analysis
python3 eda_analysis.py
```

## 🛠️ Tech Stack
- **Python:** pandas, numpy, matplotlib
- **SQL:** SQLite (joins, CTEs, window functions, subqueries)
- **Data generation:** custom seasonality-aware synthetic data generator

## 📁 Project Structure
```
ecommerce-sales-customer-analytics/
├── data/
│   ├── generate_data.py     # synthetic data generator
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── ecommerce.db
├── sql/
│   └── analysis_queries.sql # 10 business-question SQL queries
├── analysis/
│   └── eda_analysis.py      # cleaning + EDA + chart generation
├── charts/
│   └── *.png
└── README.md
```

## 🚀 Next Steps (if extended)
- Build a Power BI dashboard on top of `ecommerce.db` for interactive filtering by region/category
- Add a cohort retention analysis by signup month
- Predictive model for cancellation risk at order time

---
*Built by Ajay Pal Singh as a portfolio project demonstrating SQL + Python data analysis workflow, from raw data to business insight.*
