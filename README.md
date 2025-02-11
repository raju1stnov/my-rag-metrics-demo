


This repository demonstrates how to:

1. Spin up Prometheus and Grafana using Docker.
2. Generate real-time RAG (Retrieval-Augmented Generation) metrics via a Python script (`metrics-generator`).
3. Visualize metrics in Grafana.
4. Create a synthetic one-year dataset for offline analytics (e.g., BigQuery + matplotlib).

## Getting Started

### Requirements

- Docker and Docker Compose installed locally.
- Python 3.x (if you want to run the metrics generator locally).

### Step 1: Launch Prometheus and Grafana

http://localhost:9090/targets 

## **Why is Pushgateway Needed?**

Prometheus works well for  **long-running services** , but it **does not work well for short-lived jobs** like:

* **Batch jobs** (e.g., a script running once per day to process files)
* **Serverless functions** (e.g., AWS Lambda, Google Cloud Functions)
* **CI/CD pipelines** (e.g., tracking how long builds take)

**Example Problem:**

* Suppose you run a **backup job** that executes **for 30 seconds** and then exits.
* Prometheus scrapes every  **60 seconds** , so the job might  **complete before Prometheus ever scrapes its metrics** .
* As a result, **Prometheus never records any metrics** from this job.

✅ **Solution:** Instead of waiting for Prometheus to pull the data, **Pushgateway acts as a buffer** where the backup job  **pushes its metrics** . Prometheus then scrapes the Pushgateway at regular intervals.

## **How Does Pushgateway Work?**

1. **A short-lived job (e.g., a script, batch job, or function) pushes metrics** to Pushgateway  **via an HTTP request** .
2. **Pushgateway stores those metrics in memory** until Prometheus scrapes them.
3. **Prometheus scrapes Pushgateway at regular intervals** , just like any other service.
4. **Pushgateway does NOT automatically delete old metrics** , so it requires **manual cleanup** after jobs complete.

## **What is Alertmanager?**

**Alertmanager** is a Prometheus component responsible for:

* **Receiving alerts** from Prometheus.
* **Grouping, silencing, and routing alerts** (e.g., send to Slack, Email, PagerDuty, etc.).
* **Preventing alert spam** (de-duplication).
* **Managing notification timing** (e.g., don’t alert immediately on a single failure).

docker-compose up -d

* Prometheus: [http://localhost:9090]()
* Grafana: [http://localhost:3000]() (username/password = `admin/admin`)

  **prometheus query for seeing data :-**
* vectorlens_request_total
* vectorlens_request_duration_seconds
* documentstore_request_total
* chatapi_request_total
* histogram_quantile(0.95, rate(vectorlens_request_duration_seconds_bucket[5m]))
* histogram_quantile(0.95, rate(documentstore_request_duration_seconds_bucket[5m]))
* histogram_quantile(0.95, rate(chatapi_request_duration_seconds_bucket[5m]))

### Step 2: Generate Real-Time Metrics

**Run metrics generators in separate terminals** :

* cd metrics-generator

* pip install requests
* python metrics-generator/generate_vectorlens_metrics.py
  python metrics-generator/generate_docstore_metrics.py
  python metrics-generator/generate_chatapi_metrics.py
* This script pushes random RAG-related metrics (requests, latencies) to the Pushgateway.

### Step 3: Explore Grafana Dashboard

Open Grafana at [http://localhost:3000]() and look for the “RAG Demo Dashboard” (auto-provisioned). You’ll see:

* A graph of RAG requests over time
* A graph of average request latency

### Step 4: Generate One-Year Dummy Data for Offline Analysis


* This creates `rag_metrics_1yr.csv` with daily stats.
* You can import this into BigQuery or do local analysis with `matplotlib`.

### Step 5: (Optional) Local Analysis with `matplotlib`


* You’ll see a chart of requests, docstore cost, and LLM cost over a one-year timeline.

## Notes

* **Prometheus** is for real-time operational metrics.
* **BigQuery** (or CSV + Python) is for historical analytics.
* **Pushgateway** is used for sending custom metrics from Python to Prometheus.

Enjoy!




### **1. Overview of Reporting Requirements**

This document outlines the metrics and reporting requirements for the VectorLens RAG system, divided into two categories:

* **Platform Reporting** : Operational metrics for service performance (real-time).
* **Analytical Reporting** : Long-term trends and cost analysis (historical).

---

### **2. Platform Reporting (Operational Metrics)**

#### **Purpose**

Monitor real-time performance, detect anomalies, and debug issues using **Prometheus** and  **Grafana** .

#### **Key Metrics**

1. **Request Count & Throughput**
   * `vectorlens_request_total`: Total requests (counter).
   * `documentstore_request_total`: DocumentStore API requests.
   * `chatapi_request_total`: ChatAPI requests.
   * **Example Query** : `rate(vectorlens_request_total[5m])` (requests/second).
2. **Latency Metrics**
   * `vectorlens_request_duration_seconds`: End-to-end latency (histogram).
   * `documentstore_request_duration_seconds`: DocStore latency.
   * `chatapi_request_duration_seconds`: LLM latency.
   * **Example Dashboard** : Compare 95th percentile latency (`vectorlens_request_duration_seconds{quantile="0.95"}`).
3. **Error Rates**
   * `vectorlens_docstore_error_total`: DocStore errors.
   * `vectorlens_llm_error_total`: LLM errors.
   * **Example Alert** : Error rate > 1% (`(vectorlens_error_total / vectorlens_request_total) > 0.01`).

---

### **3. Prometheus Exporter Setup**

#### **Metrics Exposed by Services**

1. **VectorLens API**
   **plaintext**Copy
   ```plaintext
   - vectorlens_request_total (counter)
   - vectorlens_request_duration_seconds (histogram)
   - vectorlens_http_requests_in_progress (gauge)
   - vectorlens_docstore_error_total (counter)
   ```
2. **DocumentStore API**
   **plaintext**Copy
   ```plaintext
   - documentstore_request_total (counter)
   - documentstore_request_duration_seconds (histogram)
   - documentstore_error_total (counter)
   - documentstore_docs_returned (histogram)
   ```
3. **ChatAPI**
   **plaintext**Copy
   ```plaintext
   - chatapi_request_total (counter)
   - chatapi_request_duration_seconds (histogram)
   - chatapi_error_total (counter)
   - chatapi_tokens_input_total (counter)
   ```

---

### **4. Analytical Reporting (Historical Metrics)**

#### **Purpose**

Generate monthly/quarterly reports on cost, usage, and performance trends using  **Pub/Sub → BigQuery** .

#### **Data Structure (Per-Request Event)**

**JSON**Copy

```json
{
  "event_id": "uuid-1234",
  "user_email_id": "user@example.com",
  "org": "org-abc",
  "api_endpoint": "vectorLens",
  "operation_type": "search",
  "event_trigger_time": "2024-10-10T12:00:00Z",
  "event_completion_time": "2024-10-10T12:05:00Z",
  "docstore_elapsed_time_ms": 123,
  "docstore_num_docs_returned": 5,
  "docstore_usage_cost": 0.0012,
  "llm_elapsed_time_ms": 450,
  "llm_provider": "OpenAI",
  "llm_model": "gpt-4",
  "input_tokens": 1250,
  "output_tokens": 400,
  "total_tokens": 1650,
  "llm_usage_cost": 0.0025,
  "status": "success"
}
```

#### **Key Reports**

1. **Monthly Cost by Org**
   * Query: `SUM(llm_usage_cost + docstore_usage_cost) GROUP BY org`.
2. **Average Latency by Endpoint**
   * Query: `AVG(docstore_elapsed_time_ms) GROUP BY api_endpoint`.
3. **LLM Token Usage by Org**
   * Query: `SUM(total_tokens) GROUP BY org`.

---

### **5. Data Flow Architecture**


### **6. Example Use Cases**

1. **Real-Time Alerting** :

* Alert if `vectorlens_request_duration_seconds{quantile="0.95"}` exceeds 2 seconds.

1. **Cost Analysis** :

* Calculate monthly LLM costs per org using BigQuery:
  **sql**Copy
  ```sql
  SELECT org, SUM(llm_usage_cost) AS total_cost
  FROM `project.dataset.metrics`
  WHERE DATE(event_trigger_time) >= '2024-10-01'
  GROUP BY org;
  ```

---

### **7. Tools & Integration**

* **Prometheus/Grafana** : Real-time dashboards and alerts.
* **Pub/Sub/BigQuery** : Historical storage and analytics.
* **Cloud Function** : Validates and enriches metrics data.

---

This format ensures clarity for stakeholders, with technical details separated from high-level summaries. Use Confluence’s **tables** for metrics, **code blocks** for JSON/SQL examples, and **diagrams** for architecture.


Here’s a structured, presentation-ready format for Confluence, organized into sections with clear headings, bullet points, and examples:

---

### **1. Overview of Reporting Requirements**

This document outlines the metrics and reporting requirements for the VectorLens RAG system, divided into two categories:

* **Platform Reporting** : Operational metrics for service performance (real-time).
* **Analytical Reporting** : Long-term trends and cost analysis (historical).

---

### **2. Platform Reporting (Operational Metrics)**

#### **Purpose**

Monitor real-time performance, detect anomalies, and debug issues using **Prometheus** and  **Grafana** .

#### **Key Metrics**

1. **Request Count & Throughput**
   * `vectorlens_request_total`: Total requests (counter).
   * `documentstore_request_total`: DocumentStore API requests.
   * `chatapi_request_total`: ChatAPI requests.
   * **Example Query** : `rate(vectorlens_request_total[5m])` (requests/second).
2. **Latency Metrics**
   * `vectorlens_request_duration_seconds`: End-to-end latency (histogram).
   * `documentstore_request_duration_seconds`: DocStore latency.
   * `chatapi_request_duration_seconds`: LLM latency.
   * **Example Dashboard** : Compare 95th percentile latency (`vectorlens_request_duration_seconds{quantile="0.95"}`).
3. **Error Rates**
   * `vectorlens_docstore_error_total`: DocStore errors.
   * `vectorlens_llm_error_total`: LLM errors.
   * **Example Alert** : Error rate > 1% (`(vectorlens_error_total / vectorlens_request_total) > 0.01`).

---

### **3. Prometheus Exporter Setup**

#### **Metrics Exposed by Services**

1. **VectorLens API**
   **plaintext**Copy
   ```plaintext
   - vectorlens_request_total (counter)
   - vectorlens_request_duration_seconds (histogram)
   - vectorlens_http_requests_in_progress (gauge)
   - vectorlens_docstore_error_total (counter)
   ```
2. **DocumentStore API**
   **plaintext**Copy
   ```plaintext
   - documentstore_request_total (counter)
   - documentstore_request_duration_seconds (histogram)
   - documentstore_error_total (counter)
   - documentstore_docs_returned (histogram)
   ```
3. **ChatAPI**
   **plaintext**Copy
   ```plaintext
   - chatapi_request_total (counter)
   - chatapi_request_duration_seconds (histogram)
   - chatapi_error_total (counter)
   - chatapi_tokens_input_total (counter)
   ```

---

### **4. Analytical Reporting (Historical Metrics)**

#### **Purpose**

Generate monthly/quarterly reports on cost, usage, and performance trends using  **Pub/Sub → BigQuery** .

#### **Data Structure (Per-Request Event)**

**JSON**Copy

```json
{
  "event_id": "uuid-1234",
  "user_email_id": "user@example.com",
  "org": "org-abc",
  "api_endpoint": "vectorLens",
  "operation_type": "search",
  "event_trigger_time": "2024-10-10T12:00:00Z",
  "event_completion_time": "2024-10-10T12:05:00Z",
  "docstore_elapsed_time_ms": 123,
  "docstore_num_docs_returned": 5,
  "docstore_usage_cost": 0.0012,
  "llm_elapsed_time_ms": 450,
  "llm_provider": "OpenAI",
  "llm_model": "gpt-4",
  "input_tokens": 1250,
  "output_tokens": 400,
  "total_tokens": 1650,
  "llm_usage_cost": 0.0025,
  "status": "success"
}
```

#### **Key Reports**

1. **Monthly Cost by Org**
   * Query: `SUM(llm_usage_cost + docstore_usage_cost) GROUP BY org`.
2. **Average Latency by Endpoint**
   * Query: `AVG(docstore_elapsed_time_ms) GROUP BY api_endpoint`.
3. **LLM Token Usage by Org**
   * Query: `SUM(total_tokens) GROUP BY org`.

---

### **5. Data Flow Architecture**

Mermaid **Code**Classic**Hand Drawn**

```mermaid
graph TD
    A[User Request] --> B[VectorLens API]
    B -->|Metrics| C[Prometheus Exporter]
    C --> D[Prometheus Server]
    D --> E[Grafana Dashboards]
    B -->|Event Data| F[Pub/Sub Topic]
    F --> G[Cloud Function (Validation)]
    G --> H[BigQuery Metric Store]
    H --> I[Analytical Reports]
```

---

### **6. Example Use Cases**

1. **Real-Time Alerting** :

* Alert if `vectorlens_request_duration_seconds{quantile="0.95"}` exceeds 2 seconds.

1. **Cost Analysis** :

* Calculate monthly LLM costs per org using BigQuery:
  **sql**Copy
  ```sql
  SELECT org, SUM(llm_usage_cost) AS total_cost
  FROM `project.dataset.metrics`
  WHERE DATE(event_trigger_time) >= '2024-10-01'
  GROUP BY org;
  ```

---

### **7. Tools & Integration**

* **Prometheus/Grafana** : Real-time dashboards and alerts.
* **Pub/Sub/BigQuery** : Historical storage and analytics.
* **Cloud Function** : Validates and enriches metrics data.

---

This format ensures clarity for stakeholders, with technical details separated from high-level summaries. Use Confluence’s **tables** for metrics, **code blocks** for JSON/SQL examples, and **diagrams** for architecture.


<style>#mermaid-1739283207877{font-family:sans-serif;font-size:16px;fill:#333;}#mermaid-1739283207877 .error-icon{fill:#552222;}#mermaid-1739283207877 .error-text{fill:#552222;stroke:#552222;}#mermaid-1739283207877 .edge-thickness-normal{stroke-width:2px;}#mermaid-1739283207877 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-1739283207877 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-1739283207877 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-1739283207877 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-1739283207877 .marker{fill:#333333;}#mermaid-1739283207877 .marker.cross{stroke:#333333;}#mermaid-1739283207877 svg{font-family:sans-serif;font-size:16px;}#mermaid-1739283207877 .label{font-family:sans-serif;color:#333;}#mermaid-1739283207877 .label text{fill:#333;}#mermaid-1739283207877 .node rect,#mermaid-1739283207877 .node circle,#mermaid-1739283207877 .node ellipse,#mermaid-1739283207877 .node polygon,#mermaid-1739283207877 .node path{fill:#ECECFF;stroke:#9370DB;stroke-width:1px;}#mermaid-1739283207877 .node .label{text-align:center;}#mermaid-1739283207877 .node.clickable{cursor:pointer;}#mermaid-1739283207877 .arrowheadPath{fill:#333333;}#mermaid-1739283207877 .edgePath .path{stroke:#333333;stroke-width:1.5px;}#mermaid-1739283207877 .flowchart-link{stroke:#333333;fill:none;}#mermaid-1739283207877 .edgeLabel{background-color:#e8e8e8;text-align:center;}#mermaid-1739283207877 .edgeLabel rect{opacity:0.5;background-color:#e8e8e8;fill:#e8e8e8;}#mermaid-1739283207877 .cluster rect{fill:#ffffde;stroke:#aaaa33;stroke-width:1px;}#mermaid-1739283207877 .cluster text{fill:#333;}#mermaid-1739283207877 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:sans-serif;font-size:12px;background:hsl(80,100%,96.2745098039%);border:1px solid #aaaa33;border-radius:2px;pointer-events:none;z-index:100;}#mermaid-1739283207877:root{--mermaid-font-family:sans-serif;}#mermaid-1739283207877:root{--mermaid-alt-font-family:sans-serif;}#mermaid-1739283207877 flowchart{fill:apa;}</style>
