# Email Triage OpenEnv

An autonomous agent environment for triaging emails.

## Structure
- `server/`: FastAPI environment.
- `inference.py`: Agent with structured logging.
- `openenv.yaml`: OpenEnv config.
- `pyproject.toml`: Deps.

## Run
```bash
pip install -e .
python server/app.py
python inference.py
```
