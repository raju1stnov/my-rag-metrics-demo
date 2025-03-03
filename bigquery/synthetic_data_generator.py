import json
from datetime import datetime, timedelta
import random
import uuid

# Constants
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 3, 3)  # Today as per current date
USER_EMAIL = "user1@example.com"
SERVICE_NAME = "platform api"
API_ENDPOINT = f"/api/{SERVICE_NAME.replace(' ', '_')}"

# Variations for query_context and related fields
QUERIES = [
    {
        "query_context": "please give me the agreement documents from 2024 in csv format",
        "search_parameters": {"top_k": 5, "filter": "year=2024 AND format=csv AND document_type=agreement", "min_similarity": 0.65},
        "retrieved_docs": [{"doc_id": "KB-123", "score": 0.72}, {"doc_id": "KB-456", "score": 0.68}],
        "prompt": "Here is the user's query: 'please give me the agreement documents from 2024 in csv format'.\n\nRelevant documents:\n- KB-123 (score: 0.72)\n- KB-456 (score: 0.68)\n\nPlease generate a response based on the above documents.",
        "response_text": "Here are the agreement documents from 2024 in CSV format..."
    },
    {
        "query_context": "summarize the financial reports for Q1 2024",
        "search_parameters": {"top_k": 3, "filter": "year=2024 AND period=Q1 AND type=financial", "min_similarity": 0.70},
        "retrieved_docs": [{"doc_id": "FIN-001", "score": 0.75}, {"doc_id": "FIN-002", "score": 0.71}],
        "prompt": "Here is the user's query: 'summarize the financial reports for Q1 2024'.\n\nRelevant documents:\n- FIN-001 (score: 0.75)\n- FIN-002 (score: 0.71)\n\nPlease summarize based on the above documents.",
        "response_text": "The financial reports for Q1 2024 show..."
    },
    {
        "query_context": "find customer feedback from 2023 in text format",
        "search_parameters": {"top_k": 4, "filter": "year=2023 AND format=text AND category=feedback", "min_similarity": 0.60},
        "retrieved_docs": [{"doc_id": "FB-789", "score": 0.65}, {"doc_id": "FB-790", "score": 0.62}],
        "prompt": "Here is the user's query: 'find customer feedback from 2023 in text format'.\n\nRelevant documents:\n- FB-789 (score: 0.65)\n- FB-790 (score: 0.62)\n\nPlease generate a response based on the above documents.",
        "response_text": "Customer feedback from 2023 includes..."
    }
]

def generate_record(date):
    # Event ID: {service_name}_uuid
    event_id = f"{SERVICE_NAME.replace(' ', '_')}_{uuid.uuid4()}"

    # Random variations for latency and cost
    search_base_latency = random.randint(200, 400)
    embedding_base_latency = random.randint(100, 200)
    chat_base_latency = random.randint(200, 500)
    search_cost = round(random.uniform(0.03, 0.07), 2)
    chat_cost = round(random.uniform(0.10, 0.20), 2)

    # Select a random query variation
    query_variation = random.choice(QUERIES)
    query_context = query_variation["query_context"]
    search_params = query_variation["search_parameters"]
    retrieved_docs = query_variation["retrieved_docs"]
    prompt = query_variation["prompt"]
    response_text = query_variation["response_text"]

    # Calculate timestamps (random hour between 00:00 and 23:59)
    trigger_time = date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
    total_elapsed_time_ms = search_base_latency + embedding_base_latency + chat_base_latency
    completion_time = trigger_time + timedelta(milliseconds=total_elapsed_time_ms)

    # Construct record
    record = {
        "event_id": event_id,
        "service_name": SERVICE_NAME,
        "user_email_id": USER_EMAIL,
        "api_endpoint": API_ENDPOINT,
        "event_trigger_time": trigger_time.strftime("%Y-%m-%d %H:%M:%S"),
        "event_completion_time": completion_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "SUCCESS",
        "components": [
            {
                "component_type": "documentsearch",
                "operation_type": "vector_search",
                "elapsed_time_ms": search_base_latency + embedding_base_latency,
                "usage_cost": search_cost,
                "details": {
                    "embedding_provider": "openai",
                    "embedding_model": "gpt-4",
                    "input_tokens": random.randint(400, 600),
                    "retrieved_documents": len(retrieved_docs),
                    "document_store": "document_store_v1",
                    "search_latency_ms": search_base_latency,
                    "embedding_latency_ms": embedding_base_latency,
                    "query_context": query_context,
                    "search_parameters": search_params,
                    "retrieved_documents": retrieved_docs
                }
            },
            {
                "component_type": "chatapi",
                "operation_type": "text_generation",
                "elapsed_time_ms": chat_base_latency,
                "usage_cost": chat_cost,
                "details": {
                    "llm_provider": "openai",
                    "llm_model": "gpt-4",
                    "input_tokens": random.randint(1000, 1500),
                    "output_tokens": random.randint(200, 400),
                    "llm_context": {
                        "user_query": query_context,
                        "retrieved_documents": retrieved_docs
                    },
                    "prompt": prompt,
                    "response_text": response_text,
                    "parameters": {
                        "temperature": round(random.uniform(0.6, 0.8), 1),
                        "max_tokens": 500,
                        "top_p": 1.0
                    }
                }
            }
        ],
        "total_elapsed_time_ms": total_elapsed_time_ms,
        "total_cost": round(search_cost + chat_cost, 2),
        "no_of_token_used": sum(comp["details"]["input_tokens"] + comp["details"].get("output_tokens", 0) for comp in [
            {
                "details": {
                    "input_tokens": random.randint(400, 600),
                    "output_tokens": 0  # No output tokens for documentsearch
                }
            },
            {
                "details": {
                    "input_tokens": random.randint(1000, 1500),
                    "output_tokens": random.randint(200, 400)
                }
            }
        ])
    }

    return record

# Generate records from January 1, 2024, to March 3, 2025
records = []
current_date = START_DATE
while current_date <= END_DATE:
    # Random number of events per day (1 to 5)
    events_per_day = random.randint(1, 5)
    for _ in range(events_per_day):
        records.append(generate_record(current_date))
    current_date += timedelta(days=1)

# Save to JSON file
with open("synthetic_records_2024_to_2025.json", "w") as f:
    json.dump(records, f, indent=2)

print(f"Generated {len(records)} records from {START_DATE.date()} to {END_DATE.date()} in 'synthetic_records_2024_to_2025.json'")