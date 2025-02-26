**"API Metrics Schema Design: Scalable & Flexible Approach for Future-Proof Analytics"**

### **1. Overview**

This page outlines a schema design for storing API usage metrics in BigQuery, optimized for flexibility, scalability, and ease of integration with new components. The system is designed to support a production-grade pipeline with validation, aggregation, and analytics capabilities.

### **2. System Architecture**

**Mermaid Diagram:**

### **3. Schema Design Approaches**

**Comparison of 4 Approaches**

##### approach 1 - details as a JSON String

    CREATE TABLE`your-gcp-project-id.your-dataset.api_usage_metrics` (
	  -- Event Metadata (Common Across All Applications)
	  event_id STRING,
	  user_email_id STRING,
	  tenant_name STRING,
	  api_endpoint STRING,
	  event_trigger_time TIMESTAMP,
	  event_completion_time TIMESTAMP,
	  status STRING,

    -- Component-Specific Metrics (Repeated Field)
	  components ARRAY<STRUCT<
		component_type STRING,  -- e.g., "docstore", "llm", "governance"
		operation_type STRING,  -- e.g., "vector_search", "text_generation", "compliance_check"
		elapsed_time_ms INT64,
		usage_cost FLOAT64,

    -- Component-Specific Details (Flexible Key-Value Pairs)**details** STRING  -- JSON string for unstructured data
	  >>,

    -- Optional: Global Cost/Timing Aggregates
	  total_elapsed_time_ms INT64,
	  total_usage_cost FLOAT64
	);

    **pros:**
		Extensibility: New components can be added without schema changes.
		Backward Compatibility: Existing queries on docstore/llm still work with JSON parsing.
		Cost Aggregation: Use total_usage_cost for quick reporting, or drill into components for granularity.
		Unified Analytics: All applications share the same table structure.
**cons:**
    		query parsing is not straight forward

    **Example:**

```
{
			"component_type": "docstore", 
			"operation_type": "vector_search", 
			"elapsed_time_ms": 45, 
			"usage_cost": 0.02, 
			"details": "{"num_docs_returned": 5, "index_version": "v1.2"}"
		}
```

##### approach 2 -- Use a Nested STRUCT plus json

    approach1 details field is a STRING containing JSON, which is flexible but requires parsing and validation. Here are alternatives to make it more structured or flexible in BigQuery:

    CREATE TABLE`your-gcp-project-id.your-dataset.api_usage_metrics` (
	  -- Event Metadata (Common Across All Applications)
	  event_id STRING,
	  user_email_id STRING,
	  tenant_name STRING,
	  api_endpoint STRING,
	  event_trigger_time TIMESTAMP,
	  event_completion_time TIMESTAMP,
	  status STRING,

    -- Component-Specific Metrics
	  components ARRAY<STRUCT<
		component_type STRING,
		operation_type STRING,
		elapsed_time_ms INT64,
		usage_cost FLOAT64,
		details STRUCT<
			common_field1 STRING,  -- e.g., "model" or "policy_id"
			common_field2 INT64,   -- e.g., "input_tokens"
			extra JSON            -- For flexible fields
		>
	  >>,

    -- Optional: Global Cost/Timing Aggregates
	  total_elapsed_time_ms INT64,
	  total_usage_cost FLOAT64
	);

    **Pros:**
		Structured fields (common_field1, common_field2) are queryable directly without parsing.
		extra (JSON type, introduced in BigQuery) handles flexible fields.
	**Cons:**
		Requires defining common fields upfront, reducing flexibility for entirely new schemas.
		JSON type still needs parsing for extra, though less frequently.

**
    Example:**

```
{
		  "component_type": "llm",
		  "operation_type": "text_generation",
		  "elapsed_time_ms": 1200,
		  "usage_cost": 0.15,
		  "details": {
			"common_field1": "gpt-4",
			"common_field2": 100,
			"extra": {"output_tokens": 200, "temperature": 0.7}
		  }
		}
```

##### approach 3 - Fully Structured per Component Type

    CREATE TABLE`your-gcp-project-id.your-dataset.api_usage_metrics` (
	  -- Event Metadata (Common Across All Applications)
	  event_id STRING,
	  user_email_id STRING,
	  tenant_name STRING,
	  api_endpoint STRING,
	  event_trigger_time TIMESTAMP,
	  event_completion_time TIMESTAMP,
	  status STRING,

    -- Component-Specific Metrics (Repeated Field)
    components ARRAY<STRUCT<
		component_type STRING,
		operation_type STRING,
		elapsed_time_ms INT64,
		usage_cost FLOAT64,
		docstore_details STRUCT<num_docs_returned INT64, index_version STRING>,
		llm_details STRUCT<model STRING, input_tokens INT64, output_tokens INT64>,
		governance_details STRUCT<policy_id STRING, risk_score FLOAT64>
	  >>,

    -- Optional: Global Cost/Timing Aggregates
	  total_elapsed_time_ms INT64,
	  total_usage_cost FLOAT64
	);

    **Pros**:
		Fully typed and queryable without JSON parsing.
		Enforces structure at the schema level.
	**Cons:**
		Inflexible: adding a new component_type or changing fields requires schema evolution.
		Unused fields (e.g., docstore_details for an llm component) are NULL, wasting space.

    **Example:**
		{
		  "component_type": "docstore",
		  "operation_type": "vector_search",
		  "elapsed_time_ms": 45,
		  "usage_cost": 0.02,
		  "docstore_details": {"num_docs_returned": 5, "index_version": "v1.2"},
		  "llm_details": null,
		  "governance_details": null
	}

##### approach 4 - json Type

    CREATE TABLE`your-gcp-project-id.your-dataset.api_usage_metrics` (
	  -- Event Metadata (Common Across All Applications)
	  event_id STRING,
	  user_email_id STRING,
	  tenant_name STRING,
	  api_endpoint STRING,
	  event_trigger_time TIMESTAMP,
	  event_completion_time TIMESTAMP,
	  status STRING,

    -- Component-Specific Metrics (Repeated Field)
	  components ARRAY<STRUCT<
		component_type STRING,
		operation_type STRING,
		elapsed_time_ms INT64,
		usage_cost FLOAT64,
		details JSON
	  >>,

    -- Optional: Global Cost/Timing Aggregates
	  total_elapsed_time_ms INT64,
	  total_usage_cost FLOAT64
	);

    Pros:
		Native JSON support in BigQuery (no string parsing required).
		Fully flexible; no need to define schemas upfront.
		Queryable with JSON functions (e.g., JSON_VALUE(details, '$.model')).
	Cons:
		Still requires validation at the source to ensure required fields.
		Slightly less performant than structured fields for frequent queries.

    example:
		{
		  "component_type": "llm",
		  "operation_type": "text_generation",
		  "elapsed_time_ms": 1200,
		  "usage_cost": 0.15,
		  "details": {"model": "gpt-4", "input_tokens": 100, "output_tokens": 200}
		}

| **Approach**                | **Flexibility** | **Queryability** | **Validation Ease** | **Pros**                          | **Cons**                          |
| --------------------------------- | --------------------- | ---------------------- | ------------------------- | --------------------------------------- | --------------------------------------- |
| **1. JSON String**          | High                  | Moderate               | Moderate                  | Extensible, backward compatible         | Requires JSON parsing                   |
| **2. Nested STRUCT + JSON** | Moderate              | High                   | High                      | Structured + flexible, queryable fields | Needs common fields defined upfront     |
| **3. Fully Structured**     | Low                   | High                   | High                      | Fully typed, no parsing                 | Inflexible, schema changes needed       |
| **4. JSON Type**            | High                  | High                   | Moderate                  | Native JSON, no st                      | Requires validation for required fields |

### **4. Recommended Schema (Approach 4: JSON Type)**

**Schema Definition:**

```
CREATE TABLE `your-gcp-project-id.your-dataset.api_usage_metrics` (
  event_id STRING,
  app_name STRING,  
  user_email_id STRING,
  tenant_name STRING,
  api_endpoint STRING,
  event_trigger_time TIMESTAMP,
  event_completion_time TIMESTAMP,
  status STRING,
  components ARRAY<STRUCT<
    component_type STRING,
    operation_type STRING,
    elapsed_time_ms INT64,
    usage_cost FLOAT64,
    details JSON
  >>,
  total_elapsed_time_ms INT64,
  total_cost FLOAT64,
  no_of_token_used INT64
);
```

**Example Record:**

```
{
  "component_type": "llm",
  "operation_type": "text_generation",
  "elapsed_time_ms": 1200,
  "usage_cost": 0.15,
  "details": {
    "model": "gpt-4",
    "input_tokens": 100,
    "output_tokens": 200
  }
}
```

### 5. Some data example

```
{
    "event_id": "evt_001",
    "app_name": "sqlstar",
    "user_email_id": "user1@example.com",
    "tenant_name": "tenant_a",
    "api_endpoint": "/api/sqlstar",
    "event_trigger_time": "2024-01-01 10:00:00",
    "event_completion_time": "2024-01-01 10:00:02",
    "status": "SUCCESS",
    "components": [
        {
            "component_type": "metadata_call",
            "operation_type": "attribute_search",
            "elapsed_time_ms": 45,
            "usage_cost": 0.02,
            "details": {"returned_sql": "table attribute information", }
        },
        {
            "component_type": "llm_call",
            "operation_type": "text_generation",
            "elapsed_time_ms": 1200,
            "usage_cost": 0.15,
            "details": {"llm_provider": "openai", "model": "gpt-4", "input_tokens": 1000, "output_tokens": 2000}
        }
    ],
    "total_elapsed_time_ms": 1245,
    "total_cost": 0.17,
	"no_of_token_used": 3000
}


{
    "event_id": "evt_001",
    "app_name": "vectorlens",
    "user_email_id": "user1@example.com",
    "tenant_name": "tenant_a",
    "api_endpoint": "/api/vectorlens",
    "event_trigger_time": "2024-01-01 10:00:00",
    "event_completion_time": "2024-01-01 10:00:02",
    "status": "SUCCESS",
    "components": [
        {
            "component_type": "documentsearch",
            "operation_type": "vector_search",
            "elapsed_time_ms": 45,
            "usage_cost": 0.02,
            "details": {"llm_provider": "openai", "model": "gpt-4", "input_tokens": 1000, "output_tokens": 2000, "no_of_docs_returned": 5}
        },
        {
            "component_type": "chatapi",
            "operation_type": "text_generation",
            "elapsed_time_ms": 1200,
            "usage_cost": 0.15,
            "details": {"llm_provider": "openai", "model": "gpt-4", "input_tokens": 1000, "output_tokens": 2000}
        }
    ],
    "total_elapsed_time_ms": 1245,
    "total_cost": 0.17,
	"no_of_token_used": 3000
}
```

### **6. Schema Validation in Cloud Function**

**Validation Workflow:**

1. **Pub/Sub Trigger** : Receive event data.
2. **JSON Schema Validation** : Validate `details` field against predefined schemas for each `operation_type`.
3. **BigQuery Insert** : Insert only valid records.

**Python Cloud Function Script:**

```
import base64
import json
from google.cloud import bigquery
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BigQuery client
client = bigquery.Client()
TABLE_ID = "your-gcp-project-id.your-dataset.api_usage_metrics"

# Mandatory fields for each component
MANDATORY_FIELDS = ["component_type", "operation_type", "elapsed_time_ms", "usage_cost"]

def validate_component(component):
    """Validate a single component's mandatory fields and details."""
    # Check for mandatory fields
    for field in MANDATORY_FIELDS:
        if field not in component:
            logger.error(f"Missing mandatory field: {field}")
            return False
  
    # Check if details is a valid JSON object (dict in Python)
    details = component.get("details", {})
    if not isinstance(details, dict):
        logger.error("Details must be a dictionary (JSON object)")
        return False
  
    return True

def main(event, context):
    """Cloud Function triggered by Pub/Sub."""
    # Decode Pub/Sub message
    pubsub_message = event.get("data")
    if not pubsub_message:
        logger.error("No data in Pub/Sub message")
        return

    data = base64.b64decode(pubsub_message).decode("utf-8")
    record = json.loads(data)

    # Validate each component
    components = record.get("components", [])
    valid_components = []
    all_valid = True

    for component in components:
        if validate_component(component):
            valid_components.append(component)
        else:
            all_valid = False

    if not all_valid:
        logger.error(f"Skipping record {record['event_id']} due to invalid components")
        return

    # Prepare record for BigQuery
    bq_record = {
        "event_id": record["event_id"],
        "event_name": record["event_name"],
        "user_email_id": record["user_email_id"],
        "tenant_name": record["tenant_name"],
        "api_endpoint": record["api_endpoint"],
        "event_trigger_time": record["event_trigger_time"],
        "event_completion_time": record["event_completion_time"],
        "status": record["status"],
        "components": valid_components,
        "total_elapsed_time_ms": record["total_elapsed_time_ms"],
        "total_cost": record["total_cost"],
        "no_of_token_used": record["no_of_token_used"]
    }

    # Insert into BigQuery
    errors = client.insert_rows_json(TABLE_ID, [bq_record])
    if errors:
        logger.error(f"Failed to insert record {record['event_id']}: {errors}")
    else:
        logger.info(f"Successfully inserted record {record['event_id']}")

# Example usage (for local testing)
if __name__ == "__main__":
    sample_event = {
        "data": base64.b64encode(json.dumps({
            "event_id": "evt_001",
            "event_name": "sqlstar",
            "user_email_id": "user1@example.com",
            "tenant_name": "tenant_a",
            "api_endpoint": "/api/sqlstar",
            "event_trigger_time": "2024-01-01 10:00:00",
            "event_completion_time": "2024-01-01 10:00:02",
            "status": "SUCCESS",
            "components": [
                {
                    "component_type": "metadata_call",
                    "operation_type": "attribute_search",
                    "elapsed_time_ms": 45,
                    "usage_cost": 0.02,
                    "details": {"returned_sql": "table attribute information"}
                },
                {
                    "component_type": "llm_call",
                    "operation_type": "text_generation",
                    "elapsed_time_ms": 1200,
                    "usage_cost": 0.15,
                    "details": {"llm_provider": "openai", "model": "gpt-4", "input_tokens": 1000, "output_tokens": 2000}
                }
            ],
            "total_elapsed_time_ms": 1245,
            "total_cost": 0.17,
            "no_of_token_used": 3000
        }).encode("utf-8"))
    }
    main(sample_event, None)
```

### **7. Why This System is Scalable**

1. **Future-Proof Flexibility** :

* New components (e.g., "audio_model") can be added without schema changes.
* JSON fields allow dynamic key-value storage for component-specific metrics.

1. **Production-Grade Pipeline** :

* **Pub/Sub + Cloud Function** : Decouples data ingestion from processing.
* **Validation Layer** : Ensures data quality before storage.
* **BigQuery** : Handles large-scale analytics with native JSON support.

1. **Query Efficiency** :

* Use BigQuery’s `JSON_VALUE`/`JSON_EXTRACT` for querying JSON fields.
* Pre-aggregated fields (`total_usage_cost`) enable fast reporting.

### **8. Next Steps**

1. Finalize validation schemas for all existing components.
2. Deploy Cloud Function with monitoring (e.g., error logging to Stackdriver).
3. Create BigQuery materialized views for common queries.

---

**Conclusion**
This design balances flexibility (via JSON) and queryability (via BigQuery’s JSON functions), making it ideal for a scalable, production-grade metrics pipeline.
