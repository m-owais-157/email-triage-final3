# Email Triage OpenEnv

An OpenEnv environment for email classification — agents learn to sort emails into **spam**, **important**, or **normal** categories.

Built for the Meta PyTorch Hackathon (Scaler School of Technology).

## What It Does

The environment presents a batch of realistic emails. The agent classifies each one and gets reward feedback. Spam detection carries harsher penalties for misses since letting phishing emails through is more damaging in the real world.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/reset` | Reset env, get email batch |
| `POST` | `/step` | Submit classification |
| `GET` | `/state` | Current state |
| `GET` | `/schema` | Action/observation schema |
| `GET` | `/health` | Health check |

## Action Space

```json
{"email_id": 1, "label": "spam"}
```

Labels: `"spam"`, `"important"`, `"normal"`

## Observation Space

After `/reset`:
```json
{
  "state": {
    "emails": [{"id": 1, "text": "URGENT: Your account..."}],
    "step": 0
  }
}
```

After `/step`:
```json
{"state": {"step": 1}, "reward": 2, "done": false, "info": {"correct_label": "important"}}
```

## Reward Logic

| Outcome | Reward |
|---------|--------|
| Correct classification | +2 |
| Missed spam | -3 |
| Other incorrect | -1 |
| Invalid email_id | -2 |

## Tasks

7 emails across 3 difficulty tiers:
- **Easy** — Obvious spam (lottery, free offers)
- **Medium** — Important emails (OTPs, account warnings, deadlines)
- **Hard** — Normal emails that could be confused with spam/important

## Setup

```bash
pip install -e .
python -m server.app
```

Server runs on `http://localhost:7860`.

### Docker

```bash
docker build -t email-triage .
docker run -p 7860:7860 email-triage
```

### Inference

```bash
export ENV_URL="http://localhost:7860"
python inference.py
```

## Project Structure

```
├── server/
│   ├── __init__.py
│   ├── app.py           # Server entry point
│   └── main.py           # FastAPI app + env logic
├── inference.py           # Baseline agent
├── pyproject.toml
├── openenv.yaml
├── Dockerfile
└── uv.lock
```

## Deployment

HF Spaces: https://huggingface.co/spaces/M-OWAIS-7/email-triage-env-v1
