import time
import random
import requests

PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/documentstore"

def push_metrics():
    while True:
        requests_total = random.randint(1, 10)
        latency = round(random.uniform(0.2, 2.0), 3)

        payload = f"""
# TYPE documentstore_request_total counter
documentstore_request_total {requests_total}

# TYPE documentstore_request_duration_seconds histogram
documentstore_request_duration_seconds_bucket{{le="0.5"}} {random.randint(1, 5)}
documentstore_request_duration_seconds_bucket{{le="1.0"}} {random.randint(5, 10)}
documentstore_request_duration_seconds_bucket{{le="2.0"}} {random.randint(10, 15)}
documentstore_request_duration_seconds_bucket{{le="+Inf"}} {requests_total}
documentstore_request_duration_seconds_sum {latency * requests_total}
documentstore_request_duration_seconds_count {requests_total}
"""

        requests.put(PUSHGATEWAY_URL, data=payload, headers={'Content-Type': 'text/plain'})
        print(f"Pushed metrics: {requests_total} requests, {latency}s avg latency")
        time.sleep(5)

if __name__ == "__main__":
    push_metrics()