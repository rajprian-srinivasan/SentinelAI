# SentinelAI: Autonomous Self-Healing Site Reliability Engineering (SRE) Agent

SentinelAI is an autonomous, closed-loop Site Reliability Engineering (SRE) orchestration engine designed to continuously monitor applications, detect catastrophic runtime failures, generate AI-powered code remediations, validate patches inside an isolated sandbox, and safely deploy verified fixes through transactional, atomic updates.

---

## Architecture & System Dynamics

The engine functions as an automated control loop operating across four decoupled components:

- **Observation & Telemetry (`monitor.py`)**
  - Continuously tails production logs using system process groups (`subprocess.Popen`)
  - Processes structured JSON telemetry streams
  - Detects runtime exceptions and forwards incidents to the remediation engine

- **Automated AI Remediation (`ai_agent.py`)**
  - Dynamically maps syntax specifications using multi-language execution profiles (`.py`, `.js`, `.go`, `.cpp`)
  - Extracts target codebase context upon failure interception
  - Generates isolated root-cause code patches using an LLM

- **Isolated Sandbox Verification**
  - Writes staged changes to a temporary transaction target (`app.py.tmp`)
  - Performs syntax compilation checks
  - Executes a 3-second runtime smoke test
  - Prevents regressions before production deployment

- **Operations Control Center (`dashboard.py`)**
  - Flask-based web dashboard
  - Displays real-time telemetry streams
  - Tracks incident history and recovery success rates
  - Monitors AI token usage and operational costs
  - Provides live side-by-side patch visualization

---

## Active Feature Roadmap

###  Completed

- **Side-by-Side Patch Visualizer**
  - Integrated Diff2Html
  - Python AST parsing
  - Unified diff rendering
  - Real-time visualization of AI-generated patches prior to deployment

- **Production Cloud Target Blueprint (AWS Infrastructure)**
  - Dockerized the entire platform using Docker and Docker Compose
  - Deployed the orchestrator and Flask dashboard onto an AWS EC2 instance
  - Configured networking and port routing for public dashboard access

### 🚧 In Progress

- **Dynamic User-Submitted Code Ingestion**
  - Building frontend submission forms
  - Developing backend parsing routes
  - Allowing users to submit arbitrary broken code snippets for AI-driven analysis and patching

### 📅 Planned

- **Enterprise Multi-Language Support Matrix**
  - Expand automated healing beyond Python
  - Add support for:
    - Node.js
    - Go
    - Java
    - C++
    - Rust
    - C#

- **Diff-Based Patching**
  - Transition from full-file overwrites to Git-style line-based patches
  - Reduce token usage
  - Improve AI remediation speed

---

## Deployment & Execution Lifecycle

### Phase 1: Local Architecture (Immediate Verification)

Install dependencies:

```bash
pip install openai flask python-dotenv
```

Export environment variables:

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"
```

Start the monitoring engine and dashboard:

```bash
python3 monitor.py &
python3 dashboard.py
```

---

### Phase 2: Production Cloud Target Blueprint (AWS Infrastructure) 

- **Containerization**
  - Docker
  - Docker Compose
  - Multi-stage builds

- **Compute Instance**
  - Ubuntu AWS EC2
  - Background daemon monitoring

- **Network Routing**
  - Bound services to `0.0.0.0:5001`
  - Protected by AWS Security Groups

- **Persistent Storage & State**
  - GitHub version control
  - Rapid deployment and teardown cycles

---

### Phase 3: Dynamic User Ingestion & Interactive Patching 

- **Frontend Input UI**
  - Users can paste broken code snippets
  - Users can submit runtime error logs

- **On-Demand Orchestrator Pipeline**
  - Dynamically processes user-submitted payloads
  - Eliminates reliance on hardcoded target files

- **Real-Time Diff Rendering**
  - Instant side-by-side patch comparisons
  - Live rendering of AI-generated fixes