# SentinelAI: Autonomous Self-Healing Site Reliability Engineering (SRE) Agent

SentinelAI is an autonomous, closed-loop Site Reliability Engineering (SRE) orchestration engine designed to continuously monitor applications, detect catastrophic runtime failures, generate AI-powered code remediations, validate patches inside an isolated sandbox, and safely deploy verified fixes through transactional, atomic updates.

---

## Architecture & System Dynamics

The engine functions as an automated control loop operating across four decoupled components:

1. **Observation & Telemetry (`monitor.py`)**: Continuously tails production logs using system process groups (`subprocess.Popen`) and processes system telemetry streams using structured JSON schemas.
2. **Automated AI Remediation (`ai_agent.py`)**: Maps syntax specifications dynamically using multi-language execution profiles (`.py`, `.js`, `.go`, `.cpp`). Upon failure interception, it extracts the target codebase context to compute an isolated root-cause code patch.
3. **Isolated Sandbox Verification**: Staged changes are written to a localized transaction target (`app.py.tmp`) and passed through an isolated syntax compilation check followed by a 3-second application runtime smoke test to protect production environments from regression breaches.
4. **Operations Control Center (`dashboard.py`)**: A persistent web management panel built with Flask to expose real-time metrics tracking incident history, recovery success rates, token cost allocations, and telemetry stream tail windows.

---

## Active Feature Roadmap

* **[Completed] Side-by-Side Patch Visualizer**: Integrated Diff2Html and Python AST/unified diff parsing into the telemetry dashboard for real-time visual inspection of AI-generated code patches prior to deployment.
* **[Completed] Production Cloud Target Blueprint (AWS Infrastructure)**: Successfully packaged the engine using Docker and Docker Compose, deploying the orchestrator and Flask dashboard onto an AWS EC2 instance with proper network binding and port routing.
* **[In Progress] Dynamic User-Submitted Code Ingestion**: Building out frontend input forms and backend parsing routes to allow users to submit arbitrary, broken code snippets for live AI-driven analysis and patching.
* **[Planned] Enterprise Multi-Language Support Matrix**: Expanding the automated healing loop beyond interpreted Python runtimes to compile profiles for `Node.js`, `Go`, `Java`, `C++`, `Rust`, and `C#`.
* **[Planned] Diff-Based Patching**: Transitioning from full-file overwrites to precise Git-style line changes to lower token payload costs and increase AI remediation speeds.

---

## Deployment & Execution Lifecycle

### Phase 1: Local Architecture (Immediate Verification)

To execute the runtime simulation loop locally on your machine:

```bash
# 1. Install operational dependencies
pip install openai flask python-dotenv

# 2. Export environment variables
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"

# 3. Spin up the monitoring orchestrator and UI panel simultaneously
python3 monitor.py & python3 dashboard.py

```

### Phase 2: Production Cloud Target Blueprint (AWS Infrastructure) [Completed]

The architecture has been successfully decoupled and deployed to a cloud environment:

* **Containerization**: Packaged `monitor.py`, `dashboard.py`, and the orchestrator logic using multi-stage Dockerfiles and `docker-compose`.
* **Compute Instance (AWS EC2)**: Deployed the containerized engine onto an Ubuntu EC2 instance, running daemon monitoring loops in the background.
* **Network Routing**: Bound services to `0.0.0.0:5001` behind AWS Security Groups, allowing secure access to the telemetry dashboard via public IP.
* **Persistent Storage & State**: Codebases managed via GitHub version control with rapid spin-up and teardown cycles for cloud cost optimization.

### Phase 3: Dynamic User Ingestion & Interactive Patching [In Progress]

Extending the system beyond static workloads to support live user interactions:

* **Frontend Input UI**: Interactive submission blocks within the dashboard where users can paste arbitrary code snippets or error logs.
* **On-Demand Orchestrator Pipeline**: Adapting the backend execution engine to process user-submitted payloads dynamically instead of relying solely on hardcoded target files.
* **Real-Time Diff Rendering**: Generating instant side-by-side patch diff comparisons specifically for user-provided code in real time.