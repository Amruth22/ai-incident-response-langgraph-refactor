# AI-Powered Incident Response System - LangGraph Refactored

**LangGraph-Compliant Multi-Agent Incident Response System**

A production-ready automated incident response system built with proper separation of concerns following LangGraph best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Testing](#testing)
8. [How It Works](#how-it-works)
9. [Decision Logic](#decision-logic)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This is a **LangGraph-compliant refactoring** of an AI-powered incident response system. It automatically processes incident alerts through 3 parallel analysis agents and makes intelligent decisions about automated mitigation vs human escalation.

### What It Does

1. **Parses Alerts** - Converts unstructured alerts to structured data using AI
2. **Analyzes Logs** - Detects anomalies in system logs with retry logic
3. **Searches History** - Finds similar past incidents and solutions
4. **Determines Root Cause** - AI-powered analysis with confidence scoring
5. **Makes Decisions** - Auto-mitigation (high confidence) or escalation (low confidence)
6. **Takes Action** - Executes mitigation or escalates to humans
7. **Reports Status** - Comprehensive email notifications

**Result**: Automated incident resolution in ~6-8 seconds (3x faster than sequential).

---

## Key Features

### LangGraph-Compliant Architecture

| Component | Responsibility | What It Does | What It Doesn't Do |
|-----------|---------------|--------------|-------------------|
| **graph.py** | Orchestration | Define workflow, routing, completion tracking | Analyze logs, make decisions |
| **nodes/** | Business Logic | Log analysis, knowledge search, root cause | Track completion, decide routing |
| **agents/** | Tools | Pure analyzers, reusable functions | Manage state, know about workflow |
| **state.py** | Data Schema | Type definitions, structure | Business logic, orchestration |

### TRUE Parallel Execution

3 analysis nodes run **simultaneously** (not sequentially):

```
Incident Trigger
    ↓
[Log Analysis + Knowledge Lookup + Root Cause]  ← All parallel
    ↓
Coordinator → Decision → Mitigation/Escalation → Communicator
```

**Performance**: 6-8 seconds (vs 15-20 seconds sequential) = **3x faster**

### Intelligent Decision Making

Multi-factor decision criteria:

| Condition | Decision | Action |
|-----------|----------|--------|
| Retry count ≥ 3 | Escalation | No anomalies found |
| No anomalies detected | Escalation | Log analysis failed |
| Confidence < 0.8 | Escalation | Uncertain root cause |
| No similar incidents | Escalation | Unknown pattern |
| All conditions met | Auto-Mitigation | Execute solution |

---

## Architecture

### The Three-Layer Pattern

```
┌─────────────────────────────────────────┐
│         ORCHESTRATION LAYER             │
│            (graph.py)                   │
│  • Workflow structure                   │
│  • Routing logic                        │
│  • Completion tracking                  │
│  • NO business logic                    │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        BUSINESS LOGIC LAYER             │
│            (nodes/)                     │
│  • Alert parsing                        │
│  • Log analysis                         │
│  • Knowledge search                     │
│  • Root cause analysis                  │
│  • Decision making                      │
│  • NO orchestration                     │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│           TOOL LAYER                    │
│           (agents/)                     │
│  • Log analyzer                         │
│  • Knowledge searcher                   │
│  • AI analyzer                          │
│  • Email notifier                       │
│  • NO state management                  │
└─────────────────────────────────────────┘
```

### Project Structure

```
ai-incident-response-langgraph-refactor/
├── graph.py                    # Orchestration logic ONLY
├── state.py                    # State schema ONLY
├── config.py                   # Configuration management
├── main.py                     # Application entry point
├── tests.py                    # Comprehensive test suite
│
├── nodes/                      # Pure business logic
│   ├── incident_trigger_node.py
│   ├── log_analysis_node.py
│   ├── knowledge_lookup_node.py
│   ├── root_cause_node.py
│   ├── coordinator_node.py
│   ├── decision_node.py
│   ├── mitigation_node.py
│   ├── escalation_node.py
│   └── communicator_node.py
│
├── agents/                     # Thin, reusable tools
│   ├── log_analyzer.py
│   ├── knowledge_searcher.py
│   ├── ai_analyzer.py
│   └── email_notifier.py
│
└── utils/                      # Utilities
    └── logging_utils.py
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google AI Studio account (for Gemini API)
- Gmail account (for notifications)

### Installation

```bash
# Clone repository
git clone https://github.com/Amruth22/ai-incident-response-langgraph-refactor.git
cd ai-incident-response-langgraph-refactor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir logs
```

### Get API Keys

#### Gemini API Key
1. Go to https://aistudio.google.com
2. Click "Get API Key"
3. Create API key in new project
4. Copy key

#### Gmail App Password
1. Enable 2FA on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Copy password

### Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Gemini AI
GEMINI_API_KEY=AIza_your_key_here

# Email
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=recipient@gmail.com

# System Thresholds (optional)
CONFIDENCE_THRESHOLD=0.8
MAX_RETRIES=3
```

---

## Usage

### Process an Incident

```bash
python main.py "Payment API experiencing database connection timeouts"
```

### Run Demo

```bash
python main.py --demo
```

Then select from scenarios:
1. Database Timeout (high confidence → auto-resolve)
2. Memory Leak (medium confidence → may escalate)
3. Network Issues (complex → likely escalation)
4. Unknown Service (low confidence → escalation)

### Interactive Mode

```bash
python main.py
```

---

## Testing

### Run All Tests

```bash
python tests.py
```

### Run with Pytest

```bash
pytest tests.py -v
```

### Test Coverage

The test suite includes:
- Configuration management tests
- State creation tests
- Log analyzer tests (thin agent)
- Log analysis node tests (pure function)
- Knowledge searcher tests
- Knowledge lookup node tests
- AI analyzer tests
- Incident trigger node tests
- Decision node tests (both mitigation and escalation)
- Mitigation node tests
- Escalation node tests
- Node purity tests (verifies no orchestration in nodes)
- Full pipeline tests
- Workflow structure tests

---

## How It Works

### Step-by-Step Execution

1. **User Provides Alert**
   ```bash
   python main.py "Payment API database timeout"
   ```

2. **Graph Creates Initial State**
   ```python
   state = {
       "incident_id": "INC-20241220-ABC123",
       "raw_alert": "Payment API database timeout"
   }
   ```

3. **Incident Trigger Node Executes**
   - Uses AI to parse alert
   - Extracts service, severity, description
   - Sends initial alert email
   - Returns: `{service, severity, description}`

4. **Graph Routes to Parallel Analyses**
   ```python
   return ["log_analysis", "knowledge_lookup", "root_cause"]
   ```

5. **All 3 Nodes Execute Simultaneously**
   - Log Analysis: Detects anomalies
   - Knowledge Lookup: Finds similar incidents
   - Root Cause: AI-powered analysis
   - LangGraph merges results into state

6. **Coordinator Node Aggregates**
   - Collects all results
   - Calculates summary metrics
   - Returns: `{coordination_summary}`

7. **Decision Node Makes Decision**
   - Checks confidence threshold
   - Evaluates anomalies and history
   - Returns: `{decision, decision_metrics}`

8. **Graph Routes to Action**
   - High confidence → Mitigation Node
   - Low confidence → Escalation Node

9. **Communicator Node Reports**
   - Generates final report
   - Returns: `{final_report}`

10. **Workflow Completes**
    - Final state returned
    - Results displayed

### Email Notifications

You'll receive emails at key stages:

1. **Incident Alert** - Initial detection
2. **Log Analysis** - Anomalies detected
3. **Root Cause** - AI analysis results
4. **Mitigation** - Automated actions taken (if auto-resolved)
5. **Escalation** - Human intervention needed (if escalated)

---

## Decision Logic

### Multi-Factor Decision Criteria

```python
if retry_count >= MAX_RETRIES:
    → ESCALATE (No anomalies found after retries)
elif not anomalies_found:
    → ESCALATE (Log analysis failed)
elif confidence < CONFIDENCE_THRESHOLD:
    → ESCALATE (Low AI confidence)
elif not similar_incidents:
    → ESCALATE (No historical guidance)
else:
    → AUTO_MITIGATION (High confidence resolution)
```

### Decision Matrix

| Retry Count | Anomalies | Confidence | Similar Incidents | Decision |
|-------------|-----------|------------|-------------------|----------|
| ≥ 3 | Any | Any | Any | ESCALATE |
| Any | None | Any | Any | ESCALATE |
| < 3 | Found | < 0.8 | Any | ESCALATE |
| < 3 | Found | ≥ 0.8 | None | ESCALATE |
| < 3 | Found | ≥ 0.8 | Found | MITIGATE |

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `EMAIL_FROM` | Yes | - | Gmail address for sending |
| `EMAIL_PASSWORD` | Yes | - | Gmail app password |
| `EMAIL_TO` | Yes | - | Recipient email address |
| `CONFIDENCE_THRESHOLD` | No | 0.8 | Minimum confidence for auto-mitigation |
| `MAX_RETRIES` | No | 3 | Maximum log analysis retry attempts |
| `LOG_LEVEL` | No | INFO | Logging level |
| `LOG_FILE` | No | logs/incident_response.log | Log file path |

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Total Execution Time** | 6-8 seconds |
| **Parallel Speedup** | 3x faster than sequential |
| **Nodes Executed** | 9 nodes |
| **Parallel Analyses** | 3 simultaneous |
| **Historical Incidents** | 8 in knowledge base |

---

## Troubleshooting

### Issue: "Missing required configuration"

**Solution**: Make sure `.env` file has all required values:
```bash
cat .env
# Check that GEMINI_API_KEY, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO are set
```

### Issue: "Gemini API error"

**Solution**: 
1. Check API key is valid
2. Check you haven't exceeded free tier limits
3. Try again in a few minutes

### Issue: "Email not sending"

**Solution**:
1. Check Gmail app password is correct
2. Check 2FA is enabled on Gmail
3. Check SMTP settings in `.env`

### Issue: "Import errors when running tests"

**Solution**: Make sure you're in the project root directory:
```bash
cd ai-incident-response-langgraph-refactor
python tests.py
```

---

## Learning Value

This project demonstrates:
- LangGraph best practices
- Multi-agent system design
- Separation of concerns
- Clean architecture principles
- Pure function design
- Graph-based orchestration
- Parallel processing patterns
- Production-ready code

**Reference**: Based on [AWS LangGraph Multi-Agent Example](https://github.com/aws-samples/langgraph-multi-agent)

---

## Contributing

Contributions welcome! Please ensure:
- Nodes contain only business logic
- Graph handles all orchestration
- Agents are thin, reusable tools
- State schema has no logic
- All tests pass

---

## License

MIT License

---

## Acknowledgments

- **Mohana Priya**: For the critical feedback on LangGraph architecture
- **LangGraph Team**: For the excellent framework
- **AWS**: For the reference architecture pattern

---

## Support

For questions or issues:
1. Check this README for documentation
2. Check ARCHITECTURE.md for detailed design
3. Review inline code comments
4. Run tests to verify setup: `python tests.py`
5. Check logs in `logs/incident_response.log`

---

**Built with proper separation of concerns following LangGraph best practices**

**Status**: Production Ready
