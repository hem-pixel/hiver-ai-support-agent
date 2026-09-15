# Hiver AI Support Agent — Backend API

FastAPI backend service powering the Hiver AI Support Agent dashboard.

---

## Quickstart

### 1. Set Up Virtual Environment & Dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be live at:
- **Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## API Endpoints

### 1. Health Check
- **Endpoint**: `GET /api/health`
- **Description**: Returns operational status of the service.
- **Sample Response**:
  ```json
  {
    "status": "ok",
    "service": "hiver-ai-support-agent"
  }
  ```

### 2. Analyze Customer Message
- **Endpoint**: `POST /api/analyze`
- **Description**: Validates and analyzes an incoming customer inquiry. (Returns structured placeholders in Step 2).
- **Sample Request**:
  ```json
  {
    "message": "I was charged too much for my Uber ride"
  }
  ```
- **Sample Response**:
  ```json
  {
    "message": "I was charged too much for my Uber ride",
    "intent": null,
    "confidence": null,
    "historical_match": null,
    "similarity": null,
    "draft_reply": null,
    "decision": null,
    "decision_reason": null
  }
  ```
- **Validation**:
  - Rejects empty or whitespace-only messages with `422 Unprocessable Entity`.
