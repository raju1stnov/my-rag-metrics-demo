from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = FastAPI()

documentstore_requests_total = Counter('documentstore_requests_total', 'Total number of requests to DocumentStore API')
documentstore_request_duration = Histogram('documentstore_request_duration_seconds', 'Time taken for a document retrieval')

@app.get("/retrieve")
def retrieve():
    with documentstore_request_duration.time():
        documentstore_requests_total.inc()
        time.sleep(random.uniform(0.2, 2.0))
    return {"message": "Documents retrieved"}

@app.get("/metrics")
def metrics():
    documentstore_requests_total.inc(random.randint(0, 3))  # Randomly increment requests
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)