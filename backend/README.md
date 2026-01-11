# Backend (FastAPI + LangGraph)

## Setup
- Python 3.12+
- `pip install -r requirements.txt`
- `python main.py` (port 8000)

## Env
- `.env` at repo root: `GOOGLE_API_KEY=...`

## Rate Limit & Resilience (Vaccines #006-#007)

### Quick test (rate limit & cache)

```bash
# first call (counts toward rate limit)


# repeat same prompt (served from cache if available)
## Call Flow

# exceed limit with a loop (should return 429 after 5 in a minute)
1) Visionary → spec_document
```
2) Architect → current_plan
3) Constructor → code_diffs, build_status

## Notes
- CORS open in dev; tighten for production.
- Models centralized in `model_config.py`; do not hardcode model names.
