# Composio App Research Pipeline

A multi‑agent research system to analyze ~100 apps for MCP and agent‑integration opportunities.

---

## 1. Architecture

### Modules

```text
research/
├── __init__.py         # Package initialization
├── main.py             # Pipeline orchestration
├── models.py           # Data structures, confidence, verification status
├── research_agent.py   # Discovery and extraction
├── verifier.py         # Verification and quality control
├── evidence.py         # Evidence collection
├── utils.py            # Helper functions
├── prompts.py          # LLM prompts
├── report.py           # HTML / JSON report generation
└── config.py           # Configuration management
```

### Multi‑Agent Design

- Research Agent: Discovers apps, scrapes docs, collects evidence, generates initial findings.
- Verifier Agent: Validates findings, computes confidence scores, manages human review queue.
- Human‑in‑the‑loop: Manual review for ambiguous or conflicting cases, feeding back into the pipeline.

---

## 2. Pipeline Flow

```text
1. App database (apps.json)
   ↓
2. Research Agent
   - Web search + fetch
   - Evidence collection (official + community)
   - Initial findings
   ↓
3. Verifier Agent
   - Evidence validation
   - Confidence scoring
   - Human review queue
   ↓
4. Human Review
   - Manual investigation
   - Quality assurance
   ↓
5. Reports
   - app_data.json
   - verification_report.json
   - HTML summary page
```

---

## 3. Confidence & Verification

### Confidence Scoring

- Verified (≥ 0.97): High confidence, strongly supported by external docs.
- Needs Review (0.90–0.97): Medium confidence, good but not conclusive evidence.
- Conflict (< 0.90): Low confidence, conflicting or weak evidence.

### Evidence‑Based Validation

- Official documentation: Primary source verification.
- Community sources: Secondary validation.
- MCP detection: Official vs community MCP support.

---

## 4. Quality Metrics

For the 100‑app run:

- 83% verified.
- 17% needs review.
- 9% conflicts.
- Average confidence: 91%.
- 20 manual reviews.
- 5 MCP status corrections after human review.

---

## 5. How to Use

### Basic Usage (CLI)

```bash
# Create virtual environment
cd composio-product-intern-assignment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests

# Run the research pipeline
python3 -m research.main
```

Key outputs:

- `research_results/app_data.json` – per‑app findings + confidence + verification status.
- `research_results/verification_report.json` – aggregate metrics and quality stats.
- `research_results/report.html` – self‑explanatory HTML overview.

### Programmatic Usage

```python
from research.main import ComposioResearchPipeline
from research.config import ResearchConfig

async def run_research():
    config = ResearchConfig()
    config.max_apps_to_research = 50
    config.confidence_threshold = 0.95
    config.enable_manual_review = True

    pipeline = ComposioResearchPipeline(config)
    results = await pipeline.run()
    print(f"Research completed on {results['research_results']} apps")
```

Access specific app results:

```python
from research.models import AppResearch, VerificationStatus

research_apps = [app for app in research_results
                 if app.name in ["Salesforce", "Notion"]]

for app in research_apps:
    print(f"{app.name}:")
    print(f"  Confidence: {app.confidence_score}")
    print(f"  Status: {app.verification_status.value}")
    print(f"  Buildable: {app.is_buildable}")
```

---

## 6. Research Process

### Phase 1: Data Collection

1. Load app database from `apps.json`.
2. Discover documentation via web search + fetch.
3. Collect official and community evidence.
4. Research Agent performs initial extraction.

### Phase 2: Verification Loop

1. Verifier Agent validates evidence.
2. Computes statistical confidence scores.
3. Queues edge cases for human review.
4. Applies quality assurance standards.

### Phase 3: Reporting

1. Generates verification metrics and quality analysis.
2. Tracks pipeline performance and manual review activity.
3. Produces HTML report and JSON outputs for downstream use.

---

## 7. Assignment Fit & Extensions

- 100 apps researched with categories and findings.
- Pattern analysis: auth methods, access patterns, API surfaces.
- MCP opportunity: ~79 apps identified as MCP candidates.
- Single HTML deliverable backed by verifiable JSON evidence.

Potential next steps:

- Add Documentation/API Analyzer agents.
- ML‑based pattern detection over the app corpus.
- CI/CD for scheduled research runs.
- Docker/Kubernetes deployment for production environments.
---