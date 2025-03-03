from google.cloud import bigquery
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialize BigQuery client
client = bigquery.Client(project="your-gcp-project-id")

# BigQuery table reference
TABLE_ID = "your-gcp-project-id.your-dataset.api_usage_metrics"

# 1. Time Series Line Graph: Average Latency (ms) by Month/Day
query1 = """
SELECT
  DATE(event_trigger_time) AS date,
  FORMAT_DATE("%m/%d", event_trigger_time) AS month_day,
  component_type,
  AVG(component.elapsed_time_ms) AS avg_latency
FROM
  `{table_id}`,
  UNNEST(components) AS component
WHERE
  component_type IN ('documentsearch', 'chatapi')
GROUP BY
  date, month_day, component_type
ORDER BY
  date
""".format(table_id=TABLE_ID)

latency_df = client.query(query1).to_dataframe()

# Aggregate by month_day (ignoring component_type for simplicity, or group by type if needed)
latency_by_date = latency_df.groupby("month_day")["avg_latency"].mean().reset_index()

fig1 = px.line(
    latency_by_date,
    x="month_day",
    y="avg_latency",
    title="Average Latency (ms) Over Time by Month/Day",
    labels={"avg_latency": "Average Latency (ms)", "month_day": "Month/Day"},
    template="plotly_white"
)
fig1.update_layout(xaxis_title="Month/Day (e.g., 01/01, 03/03)", yaxis_title="Average Latency (ms)")
fig1.show()

# 2. Prompt Reporting: Tabular Data (Input, Input Tokens, Output, Output Tokens, Latency)
query2 = """
SELECT
  (SELECT details.llm_context.user_query FROM UNNEST(components) WHERE component_type = 'chatapi') AS input,
  (SELECT details.input_tokens FROM UNNEST(components) WHERE component_type = 'documentsearch') AS input_tokens,
  (SELECT details.response_text FROM UNNEST(components) WHERE component_type = 'chatapi') AS output,
  (SELECT details.output_tokens FROM UNNEST(components) WHERE component_type = 'chatapi') AS output_tokens,
  (SELECT elapsed_time_ms FROM UNNEST(components) WHERE component_type = 'chatapi') AS latency
FROM
  `{table_id}`
WHERE
  status = 'SUCCESS'
""".format(table_id=TABLE_ID)

prompt_df = client.query(query2).to_dataframe()

# Handle NULL values (optional, fill with defaults or drop)
prompt_df = prompt_df.fillna({"input": "", "input_tokens": 0, "output": "", "output_tokens": 0, "latency": 0})

# Create an interactive table with Plotly
fig2 = px.table(
    prompt_df,
    title="Prompt Reporting: Query Details",
    columns=["input", "input_tokens", "output", "output_tokens", "latency"],
    height=400
)
fig2.show()

# 3. Cost Analysis Report: Bar Chart (USD by Day)
query3 = """
SELECT
  DATE(event_trigger_time) AS date,
  SUM(component.usage_cost) AS total_cost
FROM
  `{table_id}`,
  UNNEST(components) AS component
GROUP BY
  date
ORDER BY
  date
""".format(table_id=TABLE_ID)

cost_df = client.query(query3).to_dataframe()
cost_df["date_str"] = cost_df["date"].astype(str)

fig3 = px.bar(
    cost_df,
    x="date_str",
    y="total_cost",
    title="Daily Cost Analysis (USD)",
    labels={"total_cost": "Total Cost (USD)", "date_str": "Date"},
    template="plotly_white"
)
fig3.update_layout(xaxis_title="Date", yaxis_title="Total Cost (USD)")
fig3.show()

# 4. Tokens Used Report: Line Chart (Tokens by Day)
query4 = """
SELECT
  DATE(event_trigger_time) AS date,
  SUM(no_of_token_used) AS total_tokens
FROM
  `{table_id}`
GROUP BY
  date
ORDER BY
  date
""".format(table_id=TABLE_ID)

tokens_df = client.query(query4).to_dataframe()
tokens_df["date_str"] = tokens_df["date"].astype(str)

fig4 = px.line(
    tokens_df,
    x="date_str",
    y="total_tokens",
    title="Daily Token Usage",
    labels={"total_tokens": "Number of Tokens", "date_str": "Date"},
    template="plotly_white"
)
fig4.update_layout(xaxis_title="Date", yaxis_title="Number of Tokens")
fig4.show()