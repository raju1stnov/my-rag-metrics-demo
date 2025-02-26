## **1. API and SDK for Pub/Sub Integration**

To integrate applications like **sqlstar** and **vectorlens** with the **api_usage_metrics_topic** Pub/Sub topic, I’ll provide two production-ready Python projects: an API (**mlplatform_metrics_api**) deployed in GKE and an SDK (**mlplatform_metrics_sdk**) for client applications.

### **Project 1: **mlplatform_metrics_api****

**Purpose**

This is a Python-based API running in Google Kubernetes Engine (GKE) that acts as a wrapper around the **api_usage_metrics_topic** Pub/Sub topic. It accepts metrics data via HTTP requests and publishes them to Pub/Sub.

**GitHub Structure**

mlplatform_metrics_api/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI application
│   ├── dependencies.py # Pub/Sub client and authentication
│   └── schemas.py      # Pydantic models for payload validation
├── tests/
│   └── test_api.py     # Unit tests
├── Dockerfile          # Docker configuration for GKE
├── requirements.txt    # Dependencies
└── README.md           # Project documentation

**Sample Code**

**app/main.py**

```
from fastapi import FastAPI, Depends, HTTPException
from google.cloud import pubsub_v1
from .dependencies import get_pubsub_client, verify_api_key
from .schemas import MetricsPayload

app = FastAPI()

@app.post("/publish")
async def publish_metrics(payload: MetricsPayload, api_key: str = Depends(verify_api_key)):
    try:
        publisher = get_pubsub_client()
        topic_path = publisher.topic_path("your-gcp-project-id", "api_usage_metrics_topic")
        data = payload.json().encode("utf-8")
        publisher.publish(topic_path, data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish: {str(e)}")
```

**app/dependencies.py**

```
from google.cloud import pubsub_v1
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

API_KEY = "your-api-key"  # Use Secret Manager in production

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_pubsub_client():
    return pubsub_v1.PublisherClient()

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```



app/schemas.py

```
from pydantic import BaseModel
from typing import List, Dict, Any

class Component(BaseModel):
    component_type: str
    operation_type: str
    elapsed_time_ms: int
    usage_cost: float
    details: Dict[str, Any]

class MetricsPayload(BaseModel):
    event_id: str
    app_name: str
    user_email_id: str
    tenant_name: str
    api_endpoint: str
    event_trigger_time: str
    event_completion_time: str
    status: str
    components: List[Component]
    total_elapsed_time_ms: int
    total_cost: float
    no_of_token_used: int
```


**Deployment**

* **Dockerfile** : Build a container image with Python 3.9, install dependencies from **requirements.txt**, and run **uvicorn** to serve the FastAPI app.
* **GKE** : Deploy as a Kubernetes service with an ingress for external access. Use horizontal pod autoscaling for production readiness.

**requirements.txt**

fastapi==0.103.0
uvicorn==0.23.2
google-cloud-pubsub==2.18.0
pydantic==1.10.12


### Project 2: **mlplatform_metrics_sdk**

**Purpose**

This is a Python SDK that simplifies sending metrics to the **mlplatform_metrics_api** for applications like **sqlstar** and **vectorlens**.

**GitHub Structure**

mlplatform_metrics_sdk/
├── mlplatform_metrics/
│   ├── __init__.py
│   ├── client.py       # SDK client implementation
│   └── models.py       # Data models
├── tests/
│   └── test_sdk.py     # Unit tests
├── setup.py            # For packaging as a Python module
├── requirements.txt    # Dependencies
└── README.md           # Usage instructions

**Sample Code**

**mlplatform_metrics/client.py**

```
import requests
from .models import MetricsPayload

class MetricsClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def send_metrics(self, payload: MetricsPayload):
        headers = {"X-API-Key": self.api_key}
        response = requests.post(f"{self.api_url}/publish", json=payload.dict(), headers=headers)
        response.raise_for_status()
        return response.json()
```

**mlplatform_metrics/models.py**

```
from pydantic import BaseModel
from typing import List, Dict, Any

class Component(BaseModel):
    component_type: str
    operation_type: str
    elapsed_time_ms: int
    usage_cost: float
    details: Dict[str, Any]

class MetricsPayload(BaseModel):
    event_id: str
    app_name: str
    user_email_id: str
    tenant_name: str
    api_endpoint: str
    event_trigger_time: str
    event_completion_time: str
    status: str
    components: List[Component]
    total_elapsed_time_ms: int
    total_cost: float
    no_of_token_used: int
```

**Usage Example**

```
from mlplatform_metrics.client import MetricsClient
from mlplatform_metrics.models import MetricsPayload, Component

client = MetricsClient("https://your-api-url", "your-api-key")
payload = MetricsPayload(
    event_id="evt_001",
    app_name="sqlstar",
    user_email_id="user@example.com",
    tenant_name="tenant_a",
    api_endpoint="/sql/query",
    event_trigger_time="2024-01-01 10:00:00",
    event_completion_time="2024-01-01 10:00:05",
    status="SUCCESS",
    components=[Component(
        component_type="sql_generator",
        operation_type="query_execution",
        elapsed_time_ms=5000,
        usage_cost=0.05,
        details={"query": "SELECT * FROM table"}
    )],
    total_elapsed_time_ms=5000,
    total_cost=0.05,
    no_of_token_used=0
)
response = client.send_metrics(payload)
print(response)  # {"status": "success"}
```

**requirements.txt**

```
requests==2.31.0
pydantic==1.10.12
```

**Production Readiness**

* Error handling is included via **response.raise_for_status()**.
* The SDK uses Pydantic for payload validation, ensuring data consistency.
