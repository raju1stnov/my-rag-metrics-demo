CREATE TABLE `your-gcp-project-id.your-dataset.api_usage_metrics` (
    event_id STRING,
    user_email_id STRING,
    tenant_name STRING,
    api_endpoint STRING,
    operation_type STRING,
    event_trigger_time TIMESTAMP,
    event_completion_time TIMESTAMP,
    docstore_elapsed_time_ms INT64,
    docstore_num_docs_returned INT64,
    docstore_usage_cost FLOAT64,
    llm_elapsed_time_ms INT64,
    llm_provider STRING,
    llm_model STRING,
    input_tokens INT64,
    output_tokens INT64,
    total_tokens INT64,
    llm_usage_cost FLOAT64,
    status STRING
);
