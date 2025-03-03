import random
import json
from datetime import datetime, timedelta
import pandas as pd

# Define possible components and their details
COMPONENTS = {
    "sqlstar": [
        {
            "component_type": "metadata_call",
            "operation_type": "attribute_search",
            "details_generator": lambda: {"returned_sql": "table attribute information"}
        },
        {
            "component_type": "llm_call",
            "operation_type": "text_generation",
            "details_generator": lambda: {
                "llm_provider": random.choice(["openai", "anthropic"]),
                "model": random.choice(["gpt-4", "claude-3"]),
                "input_tokens": random.randint(500, 2000),
                "output_tokens": random.randint(1000, 3000)
            }
        }
    ],
    "vectorlens": [
        {
            "component_type": "documentsearch",
            "operation_type": "vector_search",
            "details_generator": lambda: {
                "llm_provider": random.choice(["openai", "anthropic"]),
                "model": random.choice(["gpt-4", "claude-3"]),
                "input_tokens": random.randint(500, 2000),
                "output_tokens": random.randint(1000, 3000),
                "no_of_docs_returned": random.randint(1, 10)
            }
        },
        {
            "component_type": "chatapi",
            "operation_type": "text_generation",
            "details_generator": lambda: {
                "llm_provider": random.choice(["openai", "anthropic"]),
                "model": random.choice(["gpt-4", "claude-3"]),
                "input_tokens": random.randint(500, 2000),
                "output_tokens": random.randint(1000, 3000)
            }
        }
    ]
}

# Other parameters
APP_NAMES = ["sqlstar", "vectorlens"]
USERS = [f"user{i}@example.com" for i in range(1, 11)]
TENANTS = ["tenant_a", "tenant_b", "tenant_c", "tenant_d"]
API_ENDPOINTS = {event: f"/api/{event}" for event in APP_NAMES}

def generate_random_timestamp(month, year=2024):
    start = datetime(year, month, 1)
    end = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()) - 1)
    return start + timedelta(seconds=random_seconds)

def generate_record(event_id, month):
    app_name = random.choice(APP_NAMES)
    components_used = COMPONENTS[app_name]
    components = []
    total_elapsed_time_ms = 0
    total_cost = 0.0
    no_of_token_used = 0

    for comp in components_used:
        elapsed_time_ms = random.randint(20, 2000)
        usage_cost = round(random.uniform(0.01, 0.20), 2)
        details = comp["details_generator"]()
        if "input_tokens" in details:
            no_of_token_used += details["input_tokens"] + details.get("output_tokens", 0)
        components.append({
            "component_type": comp["component_type"],
            "operation_type": comp["operation_type"],
            "elapsed_time_ms": elapsed_time_ms,
            "usage_cost": usage_cost,
            "details": details
        })
        total_elapsed_time_ms += elapsed_time_ms
        total_cost += usage_cost

    trigger_time = generate_random_timestamp(month)
    completion_time = trigger_time + timedelta(milliseconds=total_elapsed_time_ms)

    return {
        "event_id": f"evt_{event_id:05d}",
        "app_name": app_name,
        "user_email_id": random.choice(USERS),
        "tenant_name": random.choice(TENANTS),
        "api_endpoint": API_ENDPOINTS[app_name],
        "event_trigger_time": trigger_time.strftime("%Y-%m-%d %H:%M:%S"),
        "event_completion_time": completion_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": random.choice(["SUCCESS", "FAILURE"]),
        "components": components,
        "total_elapsed_time_ms": total_elapsed_time_ms,
        "total_cost": total_cost,
        "no_of_token_used": no_of_token_used
    }

# Generate data for each month of 2024
all_records = []
for month in range(1, 13):
    num_records = random.randint(1000, 5000)
    monthly_records = [generate_record(i + 1, month) for i in range(num_records)]
    all_records.extend(monthly_records)

# Convert to DataFrame and save to CSV
df = pd.DataFrame(all_records)
df.to_csv("synthetic_data_2024.csv", index=False)
print("Generated synthetic data for 2024 and saved to 'synthetic_data_2024.csv'")