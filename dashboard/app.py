import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.ab_test import run_ab_test

st.set_page_config(page_title="ShopPulse Analytics", layout="wide")

@st.cache_data
def load_data(query_file):

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        r"SERVER=BLINDXDHAKAD\SQLEXPRESS;"
        "DATABASE=ShopPulse;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    engine = create_engine(
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(connection_string)
    )

    with open(query_file, "r") as f:
        query = f.read()

    return pd.read_sql(query, engine)
st.title("ShopPulse: Product Analytics & Experimentation")

tab1, tab2, tab3, tab4 = st.tabs(["Cohort Retention", "Funnel Drop-off", "RFM Segmentation", "A/B Testing"])

with tab1:
    st.header("Cohort Retention Analysis")
    st.markdown("Tracks how well we are retaining users who made their first purchase in a given month.")
    try:
        cohorts = load_data('sql/cohorts.sql')
        # Create pivot table for heatmap
        cohort_pivot = cohorts.pivot(index='first_purchase_month', columns='month_number', values='retention_percent')
        cohort_pivot.index = pd.to_datetime(cohort_pivot.index).strftime('%Y-%m')
        
        fig = px.imshow(cohort_pivot, 
                        labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention %"),
                        color_continuous_scale='YlGnBu')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Insight: Look for vertical bands of color to identify macro-trends, and horizontal bands to see if specific cohorts are exceptionally loyal.")
    except Exception as e:
        st.error(f"Error loading cohorts: {e}")

with tab2:
    st.header("Funnel Drop-off Analysis")
    st.markdown("Shows exactly where we lose shoppers in the checkout journey.")
    try:
        funnel = load_data('sql/funnel.sql')
        fig = go.Figure(go.Funnel(
            y = funnel['step_name'],
            x = funnel['user_count'],
            textinfo = "value+percent initial"
        ))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Insight: The step with the largest percentage drop is the biggest opportunity for product improvement.")
    except Exception as e:
        st.error(f"Error loading funnel: {e}")

with tab3:
    st.header("RFM Customer Segmentation")
    st.markdown("Classifies customers based on Recency, Frequency, and Monetary value.")
    try:
        rfm = load_data('sql/rfm.sql')
        segment_counts = rfm['segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        fig = px.pie(segment_counts, names='segment', values='count', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Segment Value Breakdown")
        segment_value = rfm.groupby('segment')['monetary'].sum().reset_index()
        fig2 = px.bar(segment_value, x='segment', y='monetary', title="Total Spend by Segment",
                      color='segment', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Insight: Focus marketing spend on retaining 'Champions' and winning back high-value 'At Risk' customers.")
    except Exception as e:
        st.error(f"Error loading RFM: {e}")

with tab4:
    st.header("A/B Testing: New Checkout Button")
    st.markdown("We tested a new checkout button (Treatment) against the old one (Control). Did it actually work?")
    
    try:
        res = run_ab_test()
        if "error" in res:
            st.error(res["error"])
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Control Conversion", f"{res['control_rate']*100:.2f}%")
            col2.metric("Treatment Conversion", f"{res['treatment_rate']*100:.2f}%")
            col3.metric("Lift", f"{res['lift']*100:.2f}%")
            
            st.subheader("Statistical Confidence")
            st.write(f"**P-Value**: {res['p_value']:.2e}")
            st.write(f"**Power**: {res['power']*100:.1f}%")
            
            if res['significant']:
                st.success(f"Result: STATISTICALLY SIGNIFICANT. The treatment outperformed the control, and we have enough data to be confident it wasn't just luck (Power > 80%, p < 0.05).")
            else:
                st.warning("Result: NOT SIGNIFICANT. Either the change had no real effect, or we don't have enough data yet.")
                
            # Confidence interval plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[res['control_rate'], res['treatment_rate']],
                y=['Control', 'Treatment'],
                error_x=dict(
                    type='data',
                    symmetric=False,
                    array=[res['ci_control'][1]-res['control_rate'], res['ci_treatment'][1]-res['treatment_rate']],
                    arrayminus=[res['control_rate']-res['ci_control'][0], res['treatment_rate']-res['ci_treatment'][0]]
                ),
                mode='markers',
                marker=dict(size=10, color=['blue', 'green'])
            ))
            fig.update_layout(title="Conversion Rate with 95% Confidence Intervals", xaxis_title="Conversion Rate")
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error running A/B test: {e}")
