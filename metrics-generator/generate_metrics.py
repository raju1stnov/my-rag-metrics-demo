import time
import random
import requests

PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/rag_demo"

def generate_metrics():
    """
    Simulates random RAG usage metrics and pushes them to the Pushgateway.
    """

    while True:
        # Simulate number of requests in last interval
        requests_count = random.randint(0, 10)
        # Simulate average request latency in seconds
        avg_latency = round(random.uniform(0.1, 1.5), 3)

        payload = f"""
# TYPE rag_requests_total counter
rag_requests_total {requests_count}

# TYPE rag_request_duration_seconds gauge
rag_request_duration_seconds {avg_latency}
"""

        # Push to pushgateway
        try:
            print(f"Sending payload:\n{payload}")
            resp = requests.post(PUSHGATEWAY_URL, data=payload)
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.text}")
            print(f"Response Headers: {resp.headers}")
            if resp.status_code in [200, 202]:
                print(f"Pushed metrics: {requests_count} requests, {avg_latency}s avg latency")
            else:
                print(f"Failed to push metrics. Status code: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while pushing metrics: {e}")

        time.sleep(5)  # Sleep 5 seconds

if __name__ == "__main__":
    generate_metrics()