# SentinelAI: Autonomous Self-Healing Site Reliability Engineering (SRE) Agent

An autonomous, closed-loop SRE orchestration engine designed to monitor microservices, intercept catastrophic runtime exceptions, validate failure remediations in an isolated sandbox, and dynamically apply LLM-driven patches via transactional atomic code deployments.

## Architecture & System Dynamics

The engine functions as an automated control loop operating across four decoupled components:

1. **Observation & Telemetry (`monitor.py`)**: Continuously tails production logs using system process groups (`subprocess.Popen`) and processes system telemetry streams using structured JSON schemas.
2. **Automated AI Remediation (`ai_agent.py`)**: Maps syntax specifications dynamically using multi-language execution profiles (`.py`, `.js`, `.go`, `.cpp`). Upon failure interception, it extracts the target codebase context to compute an isolated root-cause code patch.
3. **Isolated Sandbox Verification**: Staged changes are written to a localized transaction target (`app.py.tmp`) and passed through an isolated syntax compilation check followed by a 3-second application runtime smoke test to protect production environments from regression breaches.
4. **Operations Control Center (`dashboard.py`)**: A persistent web management panel built with Flask to expose real-time metrics tracking incident history, recovery success rates, token cost allocations, and telemetry stream tail windows.

---

## Active Feature Roadmap

* **[Completed] Side-by-Side Patch Visualizer**: Integrated Diff2Html and Python AST/unified diff parsing into the telemetry dashboard for real-time visual inspection of AI-generated code patches prior to deployment.
* **[In Progress] Enterprise Multi-Language Support Matrix**: Expanding the automated healing loop beyond interpreted Python runtimes. Active development is underway to test and harden compilation and runtime smoke test profiles for compiled binaries and strict runtimes (`Node.js`, `Go`, `Java`, `C++`, `Rust`, and `C#`).
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

### Phase 2 (In Progress): Production Cloud Target Blueprint (AWS Infrastructure)

The architecture is decoupled to transition seamlessly into a cloud-native footprint:

- **Containerization**: Package `monitor.py`, `app.py`, and `dashboard.py` using multi-stage Dockerfiles to isolate language dependencies and environment profiles.
- **Compute Instance (AWS EC2)**: Deploy the containerized engine onto an EC2 instance (`t3.micro`) using docker-compose to run the daemon monitoring loops in the background.
- **Network Routing**: Expose port 5001 behind an AWS Security Group or an Application Load Balancer (ALB) to access the telemetry dashboard securely via a public IP.
- **Production Log Ingestion**: Swap out the local flat-file log tailing engine for an AWS CloudWatch Logs or an ElasticSearch data ingestion agent to capture errors from live cloud microservices.