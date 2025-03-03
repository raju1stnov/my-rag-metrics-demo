import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load synthetic data
with open("synthetic_records_2024_to_2025.json", "r") as f:
    data = json.load(f)

# Normalize the data into a DataFrame
records = []
for record in data:
    for component in record["components"]:
        record["component_type"] = component["component_type"]
        record["component_elapsed_time_ms"] = component["elapsed_time_ms"]
        record["component_usage_cost"] = component["usage_cost"]
        record["component_details"] = component["details"]
        records.append(record.copy())
df = pd.DataFrame(records)

# Convert event_trigger_time to datetime for grouping
df["event_trigger_time"] = pd.to_datetime(df["event_trigger_time"])
df["date"] = df["event_trigger_time"].dt.date
df["month_day"] = df["event_trigger_time"].dt.strftime("%m/%d")

# 1. Time Series Line Graph: Average Latency (ms) by Month/Day
latency_df = df[df["component_type"].isin(["documentsearch", "chatapi"])]  # Focus on relevant components
latency_by_date = latency_df.groupby("month_day")["component_elapsed_time_ms"].mean().reset_index()

fig1 = px.line(
    latency_by_date,
    x="month_day",
    y="component_elapsed_time_ms",
    title="Average Latency (ms) Over Time by Month/Day",
    labels={"component_elapsed_time_ms": "Average Latency (ms)", "month_day": "Month/Day"},
    template="plotly_white"
)
fig1.update_layout(xaxis_title="Month/Day (e.g., 01/01, 03/03)", yaxis_title="Average Latency (ms)")
fig1.show()

# 2. Prompt Reporting: Tabular Data (Input, Input Tokens, Output, Output Tokens, Latency)
# Simulate data based on your SQL query
prompt_data = []
for record in data:
    if record["status"] == "SUCCESS":
        docsearch_comp = next((c for c in record["components"] if c["component_type"] == "documentsearch"), None)
        chat_comp = next((c for c in record["components"] if c["component_type"] == "chatapi"), None)
        if docsearch_comp and chat_comp:
            prompt_data.append({
                "input": chat_comp["details"].get("llm_context", {}).get("user_query", ""),
                "input_tokens": docsearch_comp["details"].get("input_tokens", 0),
                "output": chat_comp["details"].get("response_text", ""),
                "output_tokens": chat_comp["details"].get("output_tokens", 0),
                "latency": chat_comp["elapsed_time_ms"]
            })

prompt_df = pd.DataFrame(prompt_data)

# Create an interactive table with Plotly
fig2 = px.table(
    prompt_df,
    title="Prompt Reporting: Query Details",
    columns=["input", "input_tokens", "output", "output_tokens", "latency"],
    height=400
)
fig2.show()

# 3. Cost Analysis Report: Bar Chart (USD by Day)
cost_by_date = df.groupby("date")["component_usage_cost"].sum().reset_index()
cost_by_date["date_str"] = cost_by_date["date"].astype(str)

fig3 = px.bar(
    cost_by_date,
    x="date_str",
    y="component_usage_cost",
    title="Daily Cost Analysis (USD)",
    labels={"component_usage_cost": "Total Cost (USD)", "date_str": "Date"},
    template="plotly_white"
)
fig3.update_layout(xaxis_title="Date", yaxis_title="Total Cost (USD)")
fig3.show()

# 4. Tokens Used Report: Line Chart (Tokens by Day)
tokens_by_date = df.groupby("date")["no_of_token_used"].sum().reset_index()
tokens_by_date["date_str"] = tokens_by_date["date"].astype(str)

fig4 = px.line(
    tokens_by_date,
    x="date_str",
    y="no_of_token_used",
    title="Daily Token Usage",
    labels={"no_of_token_used": "Number of Tokens", "date_str": "Date"},
    template="plotly_white"
)
fig4.update_layout(xaxis_title="Date", yaxis_title="Number of Tokens")
fig4.show()