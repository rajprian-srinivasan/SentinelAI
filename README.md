````markdown
# SentinelAI: Autonomous Self-Healing Site Reliability Engineering (SRE) Agent

SentinelAI is an autonomous, closed-loop Site Reliability Engineering (SRE) orchestration engine designed to continuously monitor applications, detect catastrophic runtime failures, generate AI-powered code remediations, validate patches inside an isolated sandbox, and safely deploy verified fixes through transactional, atomic updates.

---

## Key Features

- **Enterprise Polyglot Support (12 Runtimes):** Native language profiles supporting Python (`.py`), Node.js/JavaScript (`.js`), TypeScript (`.ts`), Go (`.go`), Java (`.java`), C++ (`.cpp`), C (`.c`), Rust (`.rs`), C# (`.cs`), Shell/Bash (`.sh`), Ruby (`.rb`), and PHP (`.php`).
- **Language-Native Incident Header Injector:** Generates top-of-file SRE incident reports dynamically using the appropriate language comment syntax (`#`, `//`, `///`) without breaking executable code.
- **Interactive Remediation Workbench:** Web-based ingestion platform where engineers can submit broken code snippets and stack traces in any supported language for instant AI analysis and remediation.
- **Side-by-Side Visual Diffing:** Integrated `Diff2Html` visualizer displaying side-by-side patch diffs and clean, executable source code ready for production deployment.
- **Cost Observability & Telemetry:** Real-time token usage tracking (Prompt, Completion, and Total) to maintain API cost control during autonomous healing cycles.
- **Compiler & Syntax Validation Loop (In Progress):** Automated pre-flight checks using native compiler flags (`g++ -fsyntax-only`, `python3 -m py_compile`, `go vet`, `rustc`, etc.) before deploying patches.

---

## Architecture & System Dynamics

The engine functions as an automated control loop operating across four decoupled components:

1. **Observation & Telemetry (`monitor.py`):** Continuously tails production logs using system process groups (`subprocess.Popen`) and processes system telemetry streams using structured JSON schemas.
2. **Centralized Configuration & Language Matrix (`config.py`):** Single source of truth defining runtime profiles, execution commands, compilation validation flags, and comment syntaxes across 12 programming languages.
3. **Automated AI Remediation (`ai_agent.py`):** Queries language-specific profiles to extract target codebase context, inspect error logs, and generate isolated root-cause code patches with language-native report headers.
4. **Operations Control Center (`dashboard.py`):** A persistent web management panel built with Flask to expose real-time metrics, incident history, recovery success rates, token cost allocations, and an interactive multi-language remediation workbench.

---

## Dynamic Multi-Language Matrix

SentinelAI automatically matches target runtimes with their native comment syntax and compiler validation pipelines:

| Language Profile | File Extension | Comment Syntax | Pre-Flight Validation Command |
| :--- | :--- | :--- | :--- |
| **Python** | `.py` | `#` | `python3 -m py_compile` |
| **Node.js / JS** | `.js` | `//` | `node --check` |
| **TypeScript** | `.ts` | `//` | `npx tsc --noEmit` |
| **Go** | `.go` | `//` | `go vet` |
| **Java** | `.java` | `//` | `javac` |
| **C++** | `.cpp` | `//` | `g++ -fsyntax-only` |
| **C** | `.c` | `//` | `gcc -fsyntax-only` |
| **Rust** | `.rs` | `///` | `rustc --gated-syntax-check` |
| **C#** | `.cs` | `//` | `dotnet build --no-incremental` |
| **Shell / Bash** | `.sh` | `#` | `bash -n` |
| **Ruby** | `.rb` | `#` | `ruby -c` |
| **PHP** | `.php` | `//` | `php -l` |

---

## Deployment & Execution Lifecycle

### Local Architecture Execution

To execute the self-healing dashboard and orchestrator:

```bash
# 1. Install operational dependencies
pip install openai flask python-dotenv

# 2. Export environment variables
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"
export TARGET_FILE="app.py"  # Optional override

# 3. Spin up the Dashboard Panel
python3 dashboard.py
```

Access the Operations Control Center on port `5001` in your browser.

---

## Active Feature Roadmap

- **[Completed] Dynamic Multi-Language Ingestion Matrix:** Expanded target runtime matrix to support 12 enterprise languages with dynamic HTML selection driven directly from `config.py`.
- **[Completed] Language-Native Header Generator:** Automated dynamic comment syntax matching (`#`, `//`, `///`) for top-of-file autonomous incident reports across all language profiles.
- **[Completed] Side-by-Side Patch Visualizer:** Integrated Diff2Html and Python unified diff parsing into the telemetry dashboard for real-time visual inspection of code patches.
- **[Completed] Production Cloud Target Blueprint (AWS Infrastructure):** Packaged the engine using Docker and Docker Compose, deploying the orchestrator and Flask dashboard onto an AWS EC2 instance.
- **[In Progress] Pre-Flight Compilation Verification Loop:** Hooking `config.LANGUAGE_PROFILES` validation commands (`gcc`, `javac`, `go vet`, `tsc`, `rustc`) into an isolated pre-flight execution sandbox to verify patches before outputting to the user.
- **[Planned] Diff-Based Patching:** Transitioning from full-file overwrites to precise Git-style line changes to lower token payload costs and increase remediation speed.
````
