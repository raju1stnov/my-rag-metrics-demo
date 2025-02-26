"""
A line chart showing monthly LLM token usage, segmented by tenant and application

"""


import json

# Extract LLM component data
llm_data = []
for idx, row in df.iterrows():
    components = json.loads(row["components"])
    for comp in components:
        if comp["component_type"] in ["llm_call", "chatapi"]:
            tokens = comp["details"].get("input_tokens", 0) + comp["details"].get("output_tokens", 0)
            llm_data.append({
                "tenant_name": row["tenant_name"],
                "app_name": row["app_name"],
                "month": row["month"],
                "tokens": tokens
            })

llm_df = pd.DataFrame(llm_data)
token_usage = llm_df.groupby(["tenant_name", "month", "app_name"])["tokens"].sum().reset_index()

# Interactive line chart
fig = px.line(
    token_usage,
    x="month",
    y="tokens",
    color="app_name",
    facet_row="tenant_name",
    height=800,
    title="Monthly LLM Token Usage by Tenant and Application",
    labels={"tokens": "Total Tokens", "month": "Month", "app_name": "Application"},
    template="plotly_white"
)
fig.update_traces(mode="lines+markers")
fig.show()