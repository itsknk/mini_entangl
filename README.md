
# Mini‑Entangl

[![CI](https://github.com/itsknk/mini-entangl/actions/workflows/ci.yml/badge.svg)](https://github.com/itsknk/mini-entangl/actions/workflows/ci.yml)


**A tiny prototype showing how Entangl could detect _and_ auto‑remediate unsafe data‑center procedures.**  
Paste a Markdown Method‑of‑Procedure (MOP) → the app flags issues (power‑sequence errors, semantic duplicates) → one click rewrites the steps into a safe order.

## Features

| ✔ | Capability | Stack / Technique |
|---|-------------|------------------|
| Detect “shutdown _before_ backup online” | FastAPI heuristic rule |
| **Semantic duplicate detection** (cos > 0.50) | Sentence‑Transformers `paraphrase‑MiniLM‑L6‑v2` |
| Auto‑reordering & fix suggestions | Python rule‑engine |
| Copy‑to‑clipboard corrected MOP | SvelteKit UI |
| CI + unit tests (`pytest`) | GitHub Actions |
| Optional AWS deploy | Serverless Framework (Lambda + Amplify) |

## Quick start (local)

```bash
git clone https://github.com/itsknk/mini_entangl.git
cd mini-entangl

# --- backend ---
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload    # http://127.0.0.1:8000

# --- frontend ---
cd frontend
npm install
npm run dev -- --open                # http://127.0.0.1:5173
````

## API reference

### `POST /analyze`

```json
{ "markdown": "1. Shut down mains\n2. Start backup generator" }
```

```jsonc
{
  "steps": [
    { "number": 1, "raw": "Shut down mains" },
    { "number": 2, "raw": "Start backup generator" }
  ],
  "issues": [
    {
      "step_number": 1,
      "description": "Power shutdown occurs before backup is online",
      "suggestion": "Move this step after the generator/UPS start step"
    }
  ]
}
```

### `POST /fix`

Returns the same `issues` **plus**

```jsonc
"fixed_markdown": "1. Start backup generator\n2. Shut down mains"
```

## Running tests

```bash
pytest -q                 # 100 % coverage on rule‑engine functions
```

A CI workflow in `.github/workflows/ci.yml` runs on every push.

## (Optional) Deploy to AWS

```bash
# backend  → Lambda + API Gateway
cd backend
npm i -g serverless
serverless deploy          # prints public API URL

# frontend → Amplify static hosting
cd ../frontend
npm run build
npx amplify init && npx amplify add hosting
npx amplify publish
```

## Tech stack

* **Backend** — FastAPI · Pydantic · Sentence‑Transformers · Serverless
* **Frontend** — SvelteKit · TypeScript · vanilla CSS (Inter font)
* **CI/CD**   — GitHub Actions → pytest + (optional) deploy
* **Infra**    — AWS Lambda (arm64) · Amplify static hosting


## Road‑map

1. **Topology‑aware checks** – validate device dependencies via facility graph.
2. **LLM step‑type classifier** – fine‑tune DistilBERT to replace keyword lists.
3. **Change‑ticket webhook** – auto‑post corrected MOP to Jira / ServiceNow.
4. **Reinforcement loop** – learn from operator overrides to refine thresholds.


