# Sentinel

**GenAI-powered PII redaction gateway for enterprise compliance.**

Sentinel combines NLP detection, policy-based compliance (HIPAA/PCI-DSS/GDPR), and intelligent risk scoring to protect sensitive data. Unlike traditional redaction tools, Sentinel provides nuanced risk assessments, automatic policy recommendations, and explainable AI decisions—making compliance both secure and operationally flexible.

---

## The Problem

Organizations handling sensitive data face a compliance paradox: traditional PII redaction tools are either too rigid (over-redacting and breaking workflows) or too lenient (missing context-dependent leaks and failing audits). Manual policy configuration is error-prone, and binary pass/fail decisions lack the nuance needed for operational flexibility.

## The Solution

Sentinel uses GenAI to make intelligent, explainable redaction decisions:

- **Smart Policy Recommendation**: AI analyzes text and automatically suggests healthcare, finance, or general policies—even detecting cross-domain scenarios
- **Risk-Based Scoring**: Continuous risk assessment (0.0-1.0) with specific risk factors instead of binary leak detection
- **Tiered Responses**: Configurable thresholds trigger purge/alert/log actions based on risk levels
- **Explainable AI**: Every decision includes reasoning and confidence scores for audit trails

Built on a three-layer security architecture with production-ready features: API key authentication, immutable audit logs, health checks, and Docker deployment.

---

## Key Capabilities

### 1. Intelligent Policy Selection

AI-powered domain detection automatically recommends the right policy context:

```bash
# Ask AI which policy to use
curl -X POST http://localhost:8000/suggest-policy \
  -d '{"text": "Patient billing: credit card ending in 1234"}'

# AI Response:
{
  "recommended_context": "finance",
  "confidence": 0.88,
  "reasoning": "Mixed healthcare and finance data. Finance has stricter thresholds.",
  "detected_domains": ["healthcare", "finance"],
  "risk_warning": "Cross-domain PII - use strictest policy"
}
```

**Benefits:**
- Eliminates configuration errors during onboarding
- Automatically escalates to stricter policies for multi-domain data
- Reduces time-to-compliance from weeks to hours

### 2. Risk-Based Decision Making

Move beyond binary pass/fail with continuous risk assessment:

```bash
# Configure thresholds in .env
ENABLE_RISK_SCORING=true
RISK_THRESHOLD_PURGE=0.7   # Purge keys if risk >= 0.7
RISK_THRESHOLD_ALERT=0.5   # Alert security team if risk >= 0.5
RISK_THRESHOLD_LOG=0.3     # Log for investigation if risk >= 0.3
```

**Risk Levels:**
- **0.0-0.3**: Low risk → allow (properly redacted)
- **0.3-0.5**: Medium risk → log (contextual clues present)
- **0.5-0.7**: High risk → alert (format preservation detected)
- **0.7-1.0**: Critical risk → purge (direct PII exposure)

Every risk assessment includes explainable factors:
```json
{
  "risk_score": 0.65,
  "risk_factors": [
    "Format preservation: SSN pattern (XXX-XX-XXXX) visible",
    "Partial identifier exposed (last 4 digits)",
    "Token adjacency suggests PHI relationship"
  ],
  "recommended_action": "alert",
  "confidence": 0.92
}
```

**Benefits:**
- Tune sensitivity without code deployments
- Reduce false positives while maintaining security
- Provide audit-ready explanations for compliance
- Monitor risk trends over time via Prometheus/Grafana

### 3. Three-Layer Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Gateway                         │
│            (Authentication + Audit Logging)                  │
└──────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Layer 1:       │  │  Layer 2:       │  │  Layer 3:       │
│  NLP Detection  │─▶│  Policy Engine  │─▶│  Risk Scorer    │
│  (Presidio)     │  │  (Compliance)   │  │  (GenAI)        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              ▼
                     ┌─────────────────┐
                     │  Redis Storage  │
                     │  (24hr TTL)     │
                     └─────────────────┘
```

**Layer 1: NLP Detection** - Presidio analyzes text for 13 PII entity types (EMAIL, SSN, CREDIT_CARD, etc.)
**Layer 2: Policy Engine** - Filters entities by compliance context, confidence thresholds, restoration controls
**Layer 3: GenAI Risk Scorer** - Assigns risk scores, triggers tiered responses, provides explainability

### 4. Policy-Driven Compliance

Pre-configured contexts for major compliance frameworks:

**Healthcare Policy (HIPAA)**
- Redacts: PERSON, US_SSN, DATE_TIME, LOCATION, PHONE, EMAIL, IP_ADDRESS
- Min confidence: 0.5 (reduce false positives)
- Restoration: Permanently disabled

**Finance Policy (PCI-DSS)**
- Redacts: CREDIT_CARD, IBAN_CODE, US_BANK_NUMBER, US_SSN, DRIVER_LICENSE
- Min confidence: 0.6 (high-security threshold)
- Restoration: Permanently disabled

**General Policy**
- Redacts: 13 entity types (broad coverage)
- Restoration: Disabled by default (opt-in security)

**Custom Overrides:**
```bash
# Disable specific entities
curl -X POST http://localhost:8000/redact \
  -d '{
    "text": "Meeting on 2024-01-15 with john@example.com",
    "policy": {
      "context": "general",
      "disabled_entities": ["DATE_TIME"],
      "restoration_allowed": true
    }
  }'
```

### 5. Secure Restoration with Audit Trail

API key authentication for restoration with complete audit logging:

```bash
# Create API key for service
curl -X POST http://localhost:8000/admin/api-keys \
  -d '{"service_name": "customer-portal"}'

# Restore with authentication
curl -X POST http://localhost:8000/restore \
  -H "X-API-Key: your_key" \
  -d '{"redacted_text": "Contact [REDACTED_a1b2]"}'

# Query audit logs (HIPAA/GDPR compliance)
curl http://localhost:8000/admin/audit-logs?service_name=customer-portal
```

**Audit trail includes:** request_id, service_name, timestamp, redacted_text, restored_text, token_count, success status, IP address, user agent, risk scores

---

## Quick Start

### Docker Compose (Recommended)

```bash
# Clone and start all services
git clone <your-repo-url> && cd sentinel
docker-compose up --build

# Initialize database and generate admin API key
docker-compose exec api uv run python scripts/init_db.py
# Save the API key - you cannot retrieve it later!
```

### Test the System

```bash
# 1. Get AI policy recommendation
curl -X POST http://localhost:8000/suggest-policy \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient John Doe, SSN: 123-45-6789"}'

# Response suggests "healthcare" policy with reasoning

# 2. Redact with recommended policy
curl -X POST http://localhost:8000/redact \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient John Doe, DOB: 1990-05-15, SSN: 123-45-6789",
    "policy": {"context": "healthcare"}
  }'

# Response:
{
  "redacted_text": "Patient [REDACTED_701dac], DOB: [REDACTED_37e3d8], SSN: [REDACTED_889083]",
  "confidence_scores": {"PERSON": 0.95, "DATE_TIME": 0.85, "US_SSN": 1.0},
  "policy": {
    "context": "healthcare",
    "restoration_allowed": false
  }
}

# 3. Background risk scoring runs automatically
# Check Prometheus metrics for risk distribution
curl http://localhost:8000/metrics | grep auditor_risk
```

---

## API Reference

### Core Endpoints
- `POST /redact` - Redact PII with policy-based filtering
- `POST /restore` - **[AUTH]** Restore original text from tokens
- `POST /suggest-policy` - **[GenAI]** Get AI-powered policy recommendation
- `GET /policies` - List available policy contexts
- `GET /metrics` - Prometheus metrics (includes risk distributions)

### Health & Monitoring
- `GET /health` - Comprehensive health check (Redis, PostgreSQL, Ollama)
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

### Admin Endpoints
- `POST /admin/api-keys` - Create API key
- `GET /admin/api-keys` - List API keys (hashed)
- `DELETE /admin/api-keys/{id}` - Revoke API key
- `GET /admin/audit-logs` - Query restoration audit trail

---

## Monitoring & Observability

**Prometheus Metrics** (`http://localhost:8000/metrics`):
- `auditor_risk_scores` - Risk score distribution histogram
- `auditor_risk_actions_total{action}` - Actions taken (allow/alert/purge)
- `auditor_risk_confidence` - Assessment confidence scores
- `total_redactions` - Request counter
- `model_confidence_scores` - Presidio detection confidence

**Grafana Dashboards** (`http://localhost:3000`, admin/admin):
- Risk score trends over time
- Policy recommendation accuracy
- Entity detection breakdown
- Restoration audit trail

**Structured Logging**:
- Module-specific loggers with correlation IDs
- Configurable log levels via `LOG_LEVEL` env var
- Full stack traces for exceptions
- Risk assessment reasoning in logs

---

## Production Deployment

### Environment Configuration

```bash
# Copy example config
cp .env.example .env

# Configure GenAI features
ENABLE_RISK_SCORING=true
RISK_THRESHOLD_PURGE=0.7
RISK_THRESHOLD_ALERT=0.5
RISK_THRESHOLD_LOG=0.3
PROMPT_VERSION=v3_few_shot

# Set production credentials
POSTGRES_PASSWORD=your_secure_password
API_KEY_SECRET=your_32_byte_secret
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec api uv run python scripts/init_db.py

# Monitor logs
docker-compose logs -f api
```

### Production Considerations
- Redis persistence enabled for PII token storage
- PostgreSQL with connection pooling (SQLAlchemy)
- TLS termination via reverse proxy (nginx/traefik)
- Prometheus + Grafana monitoring stack included
- Kubernetes-ready health probes

---

## Testing & Quality

**Test Suite: 127 tests, 62% coverage, 100% pass rate**

```bash
# Run full test suite
uv run pytest --cov=app --cov-report=html --cov-report=term

# Test GenAI features specifically
uv run pytest tests/unit/test_policy_recommendation.py -v
uv run pytest tests/integration/test_policy_suggestion_api.py -v

# Run evaluation benchmark (43 test cases)
uv run python evaluation/evaluate.py
```

**Test Breakdown:**
- 71 unit tests (service layer, verification, auth, policies, risk scoring)
- 53 integration tests (API endpoints, authenticated flows, policy suggestions)
- 3 evaluation suites (precision/recall/F1, latency benchmarks)

**Coverage Highlights:**
- 100%: `policy_prompts.py`, `policy_schemas.py`, `schemas.py`
- 91%: `database.py`
- 83%: `policies.py`
- 71%: `policy_recommendation.py`
- 70%: `verification.py`

---

## Advanced LLM Prompt Engineering

### Risk Scoring Prompts

Four prompt versions for different use cases:

| Version | Strategy | Best For |
|---------|----------|----------|
| **v1_basic** | Zero-shot instruction | Fast inference, baseline |
| **v2_cot** | Chain-of-thought reasoning | Complex edge cases |
| **v3_few_shot** | 4 risk examples (low→critical) | Production use, best accuracy |
| **v4_optimized** | Concise 3-example | High-throughput scenarios |

### Policy Recommendation Prompt

Comprehensive domain detection with:
- Healthcare indicators: patient, diagnosis, medical, PHI
- Finance indicators: credit card, payment, transaction, PCI
- Multi-domain handling with risk warnings
- Keyword-based fallback for reliability

**Configure in `.env`:**
```bash
PROMPT_VERSION=v3_few_shot
ENABLE_RISK_SCORING=true
```

---

## Technical Stack

**Core:** FastAPI, Presidio (NLP), Phi-3 LLM (Ollama), Redis, PostgreSQL, SQLAlchemy
**GenAI:** LLM risk scoring, smart policy recommendation, explainable AI
**Testing:** pytest (62% coverage), fakeredis, respx, aiosqlite
**Deployment:** Docker, Docker Compose, Kubernetes-ready
**Monitoring:** Prometheus, Grafana, structured logging
**Package Management:** uv (fast Python resolver)

---

## Why Sentinel?

Traditional PII redaction tools treat every case the same—either too aggressive (breaking workflows) or too lenient (failing audits). Sentinel's GenAI approach provides:

✅ **Operational Flexibility** - Tune risk thresholds without code changes
✅ **Faster Compliance** - AI suggests correct policies automatically
✅ **Audit-Ready** - Every decision includes explainable reasoning
✅ **Production-Ready** - 62% test coverage, health checks, monitoring
✅ **Self-Hosted** - No vendor lock-in, full data control

**Use Cases:**
- Healthcare providers: HIPAA-compliant PHI redaction with automatic policy detection
- Financial institutions: PCI-DSS compliance with risk-based alerting
- SaaS platforms: Multi-tenant data protection with configurable risk levels
- Contact centers: Automatic domain detection for mixed customer data

---

## Installation & Development

### Prerequisites
- Python 3.13+ with [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose

### Local Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt
uv run python -m spacy download en_core_web_lg

# Start services
docker-compose up -d

# Run application
uvicorn app.main:app --reload
```

---

## Project Structure

```
sentinel/
├── app/
│   ├── main.py                  # FastAPI endpoints
│   ├── service.py              # Redaction service
│   ├── verification.py         # Risk scorer
│   ├── policy_recommendation.py # Smart policy suggester
│   ├── policies.py             # Policy engine
│   ├── database.py             # SQLAlchemy models
│   ├── auth.py                 # API key auth
│   ├── audit.py                # Audit logging
│   └── prompts/
│       ├── verification_prompts.py  # Risk scoring prompts
│       └── policy_prompts.py        # Domain detection prompts
├── tests/
│   ├── unit/                   # 71 unit tests
│   └── integration/            # 53 integration tests
├── evaluation/                 # Benchmark suite (43 cases)
├── docker-compose.yml          # Local development stack
└── .env.example               # Configuration template
```

---

## Contributing

Contributions welcome! Please ensure:
- Tests pass with >60% coverage (`uv run pytest --cov=app`)
- GenAI features include explainability and fallbacks
- Update documentation for user-facing changes
- Follow existing code style

---

## Acknowledgments

Built with [Microsoft Presidio](https://github.com/microsoft/presidio), [Ollama](https://ollama.ai), and [FastAPI](https://fastapi.tiangolo.com).

---

**Intelligent PII redaction with GenAI-powered compliance. Deploy with confidence.**
