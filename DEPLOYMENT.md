# Deployment Guide - Permission-Aware Enterprise RAG

## Current Status ✅

Both the **FastAPI backend** and **Streamlit frontend** are now running and ready for deployment!

### Live Services
- **FastAPI Backend**: http://127.0.0.1:8000  
  - Health check: `/health`  
  - Query endpoint: `POST /query` (requires `X-User-Role` header)  
  
- **Streamlit Frontend**: http://127.0.0.1:8501  
  - Interactive UI with role selector  
  - Real-time query demonstration  

---

## 🚀 Quick Start (Local Development)

### 1. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt            # runtime
# pip install -r requirements-dev.txt   # plus pytest, if you want to run the tests
```

### 2. Launch Backend
```bash
# With real Bedrock indexing (requires AWS credentials):
export AWS_REGION=us-east-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
uvicorn rag_app:app --reload --port 8000

# OR for testing without AWS:
export SKIP_INDEXING=1
uvicorn rag_app:app --reload --port 8000
```

### 3. Launch Frontend
```bash
streamlit run streamlit_app.py --server.port 8501
```

---

## 🐳 Docker Deployment

### Build & Run with Docker
```bash
docker build -t rbac-rag:latest .
docker run -e AWS_REGION=us-east-1 \
           -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
           -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
           -p 8080:8080 \
           rbac-rag:latest
```

**Note:** The Dockerfile currently runs FastAPI on port `8080`. Modify as needed for your infrastructure.

---

## ☁️ Cloud Deployment (AWS App Runner / Lightsail)

### Prerequisites
1. **AWS Account** with Bedrock access in `us-east-1`
2. **IAM Role** with Bedrock Converse + Embedding permissions
3. **ECR Repository** to push the Docker image

### Environment Variables Required
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<from IAM user or role>
AWS_SECRET_ACCESS_KEY=<from IAM user or role>
CHAT_MODEL_ID=us.amazon.nova-2-lite-v1:0  # (optional, default shown)
EMBED_MODEL_ID=amazon.titan-embed-text-v2:0  # (optional, default shown)
SIMILARITY_THRESHOLD=0.35  # (optional, default shown)
INPUT_COST_PER_1M=0.30  # (optional, USD per 1M input tokens)
OUTPUT_COST_PER_1M=2.50  # (optional, USD per 1M output tokens)
```

### Deployment Steps
1. Push Docker image to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag rbac-rag:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rbac-rag:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rbac-rag:latest
   ```

2. Deploy to **AWS App Runner** or **ECS + ALB**:
   - Container port: `8080`
   - CPU: 2 cores (minimum)
   - Memory: 2 GB (minimum)
   - Health check: `GET /health`

---

## ✅ CI/CD Quality Gate (GitHub Actions)

The repo has a **3-layer AI quality gate** in `.github/workflows/ai-evals.yml`:

### Layer 1: DeepEval + Unit Tests
- **Runs**: DeepEval Faithfulness metric on 30 test cases
- **Threshold**: Faithfulness ≥ 0.85 (or PR fails)
- **Report**: `deepeval-html-report` artifact

### Layer 2: Promptfoo Red-Team
- **Runs**: Jailbreak, PII leakage, prompt-injection tests
- **Models**: Nova 2 Lite vs. Claude 3.5 Haiku A/B comparison
- **Report**: `promptfoo-html-report` artifact

### Layer 3: Playwright E2E
- **Runs**: Mocked UI tests + API contract checks
- **Smoke Tests**: Live API tests (requires AWS creds)
- **Report**: `playwright-html-report` artifact

### Setup GitHub Secrets
Add these to your GitHub repository settings:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
OPENAI_API_KEY  # (for Promptfoo Claude comparison)
```

---

## 📋 Pre-Deployment Checklist

- [ ] **AWS Account Ready**
  - [ ] Bedrock access enabled in `us-east-1`
  - [ ] IAM user/role with `bedrock:InvokeModel` permissions
  - [ ] AWS credentials exported locally for testing

- [ ] **Local Testing Complete**
  - [ ] Run `pytest tests/test_rbac_unit.py` (passes)
  - [ ] Run `pytest tests/test_deepeval.py` (Faithfulness ≥ 0.85)
  - [ ] Run `npx promptfoo eval` (no PII leaks, jailbreaks blocked)
  - [ ] Run `npm run test:mocked` in `playwright/` (all UI tests pass)

- [ ] **Docker Image Ready**
  - [ ] `docker build -t rbac-rag:latest .` succeeds
  - [ ] Run container with `SKIP_INDEXING=1` for quick validation
  - [ ] Verify `GET /health` returns `{"status": "ok", ...}`

- [ ] **GitHub Actions Passing**
  - [ ] All 3 job layers pass on main branch
  - [ ] Artifact reports are generated and accessible

- [ ] **Cloud Infrastructure**
  - [ ] ECR repository created
  - [ ] App Runner or ECS cluster configured
  - [ ] Load balancer / ingress rules set up
  - [ ] Environment variables / secrets stored

- [ ] **Post-Deployment Validation**
  - [ ] Health endpoint responds
  - [ ] Query endpoint reachable with valid role headers
  - [ ] Logs visible in CloudWatch / application monitoring
  - [ ] RBAC enforcement verified (unauthenticated queries blocked)

---

## 🔐 Security Notes

1. **Never commit AWS credentials** — use IAM roles in production
2. **RBAC is enforced at the query layer** — users can only see documents for their role
3. **SIMILARITY_THRESHOLD** prevents hallucination by blocking weak matches (default: 0.35)
4. **Temperature locked to 0.0** — no creative generation, grounded answers only
5. **Audit logging** — every query logged with user, role, cited documents, and cost

---

## 🧪 Testing

### Run All Local Tests
```bash
# RBAC + Unit Tests
pytest -v tests/test_rbac_unit.py tests/test_deepeval.py

# Promptfoo Red-Team (requires Node.js 20+)
npx promptfoo@latest eval

# Playwright E2E (requires Node.js 20+)
cd playwright
npm install
npm run test:mocked  # Mocked tests (no AWS needed)
npm run test:smoke   # Live tests (requires running backend + AWS creds)
```

---

## 📞 Support & Troubleshooting

| Issue | Solution |
|-------|----------|
| **"No module named boto3"** | Run `pip install boto3` or `pip install -r requirements.txt` |
| **"ModuleNotFoundError: No module named 'bedrock'"** | Ensure boto3 is installed (Bedrock is part of boto3) |
| **Faithfulness < 0.85 in CI** | Increase `SIMILARITY_THRESHOLD` or improve prompt grounding |
| **Port 8000 already in use** | Kill existing process: `lsof -ti:8000 \| xargs kill -9` |
| **Streamlit not starting** | Ensure `export STREAMLIT_SERVER_HEADLESS=true` and check permissions |

---

## 📊 Cost Estimation (AWS Bedrock)

Using **Amazon Nova 2 Lite** (default):
- **Input**: $0.30 per 1M tokens (~670 tokens/query avg)
- **Output**: $2.50 per 1M tokens (~100 tokens/response avg)

**Per query cost**: ~$0.00024 (0.024 cents)
**1000 queries/month**: ~$0.24

---

## 📖 Architecture Reference

See [`docs/ADR-001-pre-retrieval-rbac.md`](docs/ADR-001-pre-retrieval-rbac.md) for the full architecture decision record and security model.

---

**Last Updated:** 2026-11-23  
**Status:** ✅ Ready for Production Deployment
