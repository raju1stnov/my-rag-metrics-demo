from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = FastAPI()

# Define Prometheus metrics
vectorlens_requests_total = Counter('vectorlens_requests_total', 'Total number of requests to VectorLens API')
vectorlens_request_duration = Histogram('vectorlens_request_duration_seconds', 'Time taken for a request')

@app.get("/search")
def search():
    with vectorlens_request_duration.time():
        vectorlens_requests_total.inc()
        time.sleep(random.uniform(0.1, 1.5))  # Simulate processing
    return {"message": "Search completed"}

@app.get("/metrics")
def metrics():
     # Random observation for the histogram:
    vectorlens_request_duration.observe(random.uniform(0.1, 2.0))
    # Random increment for the counter:
    vectorlens_requests_total.inc(random.randint(0, 3))  # Randomly increment requests
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)