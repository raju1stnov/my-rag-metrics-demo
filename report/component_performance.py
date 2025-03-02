"""
A box plot analyzing the distribution of elapsed_time_ms across component types to 
identify performance bottlenecks
"""

# Extract component data
component_data = []
for idx, row in df.iterrows():
    components = json.loads(row["components"])
    for comp in components:
        component_data.append({
            "component_type": comp["component_type"],
            "elapsed_time_ms": comp["elapsed_time_ms"]
        })

comp_df = pd.DataFrame(component_data)

# Box plot
fig = px.box(
    comp_df,
    x="component_type",
    y="elapsed_time_ms",
    title="Component Performance Analysis",
    labels={"elapsed_time_ms": "Elapsed Time (ms)", "component_type": "Component Type"},
    template="plotly_white",
    height=500
)
fig.update_traces(boxpoints="outliers")  # Show outliers
fig.show()