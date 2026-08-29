# ShopPulse: Product Analytics & Experimentation

ShopPulse is an end-to-end product analytics project built using the Brazilian Olist e-commerce dataset and simulated website events.

The project analyzes customer behavior, purchase funnels, retention, customer segmentation, and A/B testing using SQL Server, Python, and Streamlit.

## Architecture

- **Database:** Microsoft SQL Server
- **Analytics Layer:** SQL queries
- **Statistics Layer:** Python (pandas & statsmodels)
- **Dashboard:** Streamlit
- **Visualization:** Plotly

## Features

- **Business Metrics:** Orders, customers, revenue, average order value, and repeat customer rate.
- **Cohort Retention:** Tracks customer retention based on first purchase month.
- **Funnel Drop-off:** Identifies where customers drop off from page view to purchase.
- **RFM Segmentation:** Classifies customers using Recency, Frequency, and Monetary value.
- **A/B Testing:** Compares control and treatment conversion rates using statistical testing.

## Dataset

The project uses the Brazilian Olist e-commerce dataset with simulated website events and A/B test assignments.

Raw dataset files are kept locally and excluded from Git using `.gitignore`.

## Setup

Install dependencies:

```bash
pip install pandas numpy sqlalchemy pyodbc streamlit plotly statsmodels

Create the SQL Server database and run:

db/schema.sql

Load the data:

python load_sqlserver.py

Generate website events:

python generate_events.py

Run the dashboard:

streamlit run dashboard/app.py
Tech Stack

Python • SQL • Microsoft SQL Server • pandas • NumPy • SQLAlchemy • pyodbc • Statsmodels • Plotly • Streamlit • Git/GitHub
