import time
import random
import requests

PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/chatapi"

def push_metrics():
    while True:
        requests_total = random.randint(1, 15)
        latency = round(random.uniform(0.3, 2.5), 3)

        payload = f"""
# TYPE chatapi_request_total counter
chatapi_request_total {requests_total}

# TYPE chatapi_request_duration_seconds histogram
chatapi_request_duration_seconds_bucket{{le="0.5"}} {random.randint(1, 5)}
chatapi_request_duration_seconds_bucket{{le="1.0"}} {random.randint(5, 10)}
chatapi_request_duration_seconds_bucket{{le="2.0"}} {random.randint(10, 15)}
chatapi_request_duration_seconds_bucket{{le="+Inf"}} {requests_total}
chatapi_request_duration_seconds_sum {latency * requests_total}
chatapi_request_duration_seconds_count {requests_total}
"""

        requests.put(PUSHGATEWAY_URL, data=payload, headers={'Content-Type': 'text/plain'})
        print(f"Pushed metrics: {requests_total} requests, {latency}s avg latency")
        time.sleep(5)

if __name__ == "__main__":
    push_metrics()