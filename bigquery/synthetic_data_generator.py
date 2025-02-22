import json
import random
import uuid
from datetime import datetime, timedelta

# Generate synthetic data
num_records = 5000
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

tenants = ["org-abc", "org-def", "org-xyz"]
api_endpoints = ["vectorLens", "documentStore", "chatAPI"]
llm_providers = ["OpenAI", "Google", "Anthropic"]
llm_models = ["gpt-4", "gemini-pro", "claude-3"]

data = []
for _ in range(num_records):
    event_time = start_date + timedelta(seconds=random.randint(0, (end_date - start_date).total_seconds()))
    completion_time = event_time + timedelta(milliseconds=random.randint(100, 500))

    row = {
        "event_id": str(uuid.uuid4()),
        "user_email_id": f"user{random.randint(1, 100)}@example.com",
        "tenant_name": random.choice(tenants),
        "api_endpoint": random.choice(api_endpoints),
        "operation_type": "search",
        "event_trigger_time": event_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event_completion_time": completion_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "docstore_elapsed_time_ms": random.randint(50, 300),
        "docstore_num_docs_returned": random.randint(1, 10),
        "docstore_usage_cost": round(random.uniform(0.0005, 0.005), 6),
        "llm_elapsed_time_ms": random.randint(200, 800),
        "llm_provider": random.choice(llm_providers),
        "llm_model": random.choice(llm_models),
        "input_tokens": random.randint(500, 3000),
        "output_tokens": random.randint(100, 800),
        "total_tokens": row["input_tokens"] + row["output_tokens"],
        "llm_usage_cost": round(random.uniform(0.001, 0.010), 6),
        "status": random.choice(["success", "failure"])
    }
    data.append(row)

# Save as JSON file
with open("api_usage_metrics.json", "w") as f:
    json.dump(data, f, indent=4)

print(f"Generated {num_records} synthetic records.")
