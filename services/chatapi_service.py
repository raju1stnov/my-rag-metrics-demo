from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = FastAPI()

chatapi_requests_total = Counter('chatapi_requests_total', 'Total number of requests to ChatAPI')
chatapi_request_duration = Histogram('chatapi_request_duration_seconds', 'Time taken for a chat request')

@app.get("/chat")
def chat():
    with chatapi_request_duration.time():
        chatapi_requests_total.inc()
        time.sleep(random.uniform(0.3, 2.5))
    return {"message": "Chat response generated"}

@app.get("/metrics")
def metrics():
    chatapi_request_duration.observe(random.uniform(0.1, 2.0))
    chatapi_requests_total.inc(random.randint(0, 3))  # Randomly increment requests
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)