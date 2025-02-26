"""
An interactive stacked bar chart showing total monthly costs, broken down by tenant and application.
"""

import pandas as pd
import plotly.express as px

# Load data (replace with BigQuery query in production)
df = pd.read_csv("synthetic_data_2024.csv")  # Assume synthetic data
df["event_trigger_time"] = pd.to_datetime(df["event_trigger_time"])
df["month"] = df["event_trigger_time"].dt.to_period("M").astype(str)

# Aggregate costs
cost_metrics = df.groupby(["tenant_name", "month", "app_name"])["total_cost"].sum().reset_index()

# Interactive stacked bar chart
fig = px.bar(
    cost_metrics,
    x="month",
    y="total_cost",
    color="app_name",
    facet_col="tenant_name",
    facet_col_wrap=2,
    height=600,
    title="Monthly Cost Metrics by Tenant and Application",
    labels={"total_cost": "Total Cost ($)", "month": "Month", "app_name": "Application"},
    template="plotly_white"
)
fig.update_layout(barmode="stack", bargap=0.2, showlegend=True)
fig.show()