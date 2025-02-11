


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
