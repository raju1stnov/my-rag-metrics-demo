from google.cloud import bigquery
import json

# BigQuery Config
PROJECT_ID = "your-gcp-project-id"
DATASET_ID = "your-dataset"
TABLE_ID = "api_usage_metrics"

# Initialize BigQuery Client
client = bigquery.Client()

# Define table reference
table_ref = client.dataset(DATASET_ID).table(TABLE_ID)

# Load JSON data
with open("bigquery/api_usage_metrics.json", "r") as f:
    data = json.load(f)

# Insert data into BigQuery
errors = client.insert_rows_json(table_ref, data)
if not errors:
    print("Data successfully inserted into BigQuery!")
else:
    print(f"Errors occurred: {errors}")
