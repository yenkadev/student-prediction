# student-prediction-BE

FastAPI backend for the Early Academic Risk Warning System.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install student-prediction as editable package
pip install -e ..

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env and fill in your keys
cp .env.example .env
# Edit .env — set GEMINI_API_KEY and optionally MONGODB_URL

# 5. Start MongoDB (see section below)

# 6. Train the ML model (first time only — takes ~5 min)
python scripts/train_model.py

# 7. Start the server
uvicorn app.main:app --reload --port 8000
```

---

## MongoDB Setup (Docker)

The backend uses MongoDB to store conversations and batch job state. Collections are created automatically on first write — no migration needed.

```bash
docker run -d \
  --name mongo-student \
  -p 27017:27017 \
  mongo:7
```

The connection string for this container is:
```
mongodb://localhost:27017
```

That is the default value already in `.env.example`, so **no change is needed in `.env`** for local Docker.

**Manage the container:**
```bash
docker stop mongo-student    # stop (data is preserved)
docker start mongo-student   # restart
docker rm -f mongo-student   # delete container and all data
```

**Verify it is running:**
```bash
docker exec mongo-student mongosh --eval "db.adminCommand('ping')"
# Expected output: { ok: 1 }
```

| Setting | Value |
|---|---|
| Database name | `student_risk_db` |
| Collections | `conversations`, `batch_jobs` |
| Default URL | `mongodb://localhost:27017` |

---

## Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in the two variables:

### `GEMINI_API_KEY` (required)

Used by the chat endpoint to extract student fields from free-text messages.

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API key**
3. Copy the key — it starts with `AIza`

```
GEMINI_API_KEY=AIzaSy...
```

### `MONGODB_URL` (optional)

Defaults to `mongodb://localhost:27017` which matches the Docker container above. Only change this if you use a remote database (e.g. MongoDB Atlas):

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Go to **Database Access** → add a user with read/write role
3. Go to **Network Access** → add your IP address
4. Click **Connect** → **Drivers** → copy the connection string
5. Replace `<password>` with your user's password

```
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

**Resulting `.env` file:**
```
GEMINI_API_KEY=AIzaSy...
MONGODB_URL=mongodb://localhost:27017
```

---

## Testing the Batch Endpoint

Sample Excel files are provided in `tests/`:

```bash
# rule_based mode (7 feature columns)
curl -X POST http://localhost:8000/predict/batch \
  -F "file=@tests/test_batch_rule_based.xlsx" \
  -F "predictionType=rule_based"

# ml mode (17 feature columns)
curl -X POST http://localhost:8000/predict/batch \
  -F "file=@tests/test_batch_ml.xlsx" \
  -F "predictionType=ml"
```

Both return `{"jobId": "..."}`. Poll for results:

```bash
curl http://localhost:8000/predict/batch/<jobId>
```

The response moves from `status: "processing"` to `status: "done"` with a `results` array.
