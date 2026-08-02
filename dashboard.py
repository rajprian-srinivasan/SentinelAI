import glob
import json
import os
import difflib
from flask import Flask, jsonify, render_template_string, request
import config

try:
    from ai_agent import analyze_system_error
except ImportError:
    analyze_system_error = None

app = Flask(__name__)


def get_latest_patch_diff():
    if not os.path.exists('patches'):
        return ''

    patch_files = glob.glob('patches/*_pre_heal_*')
    if not patch_files or not os.path.exists(config.TARGET_FILE):
        return ''

    latest_backup = max(patch_files, key=os.path.getmtime)

    try:
        with open(latest_backup, 'r') as f:
            before_lines = f.readlines()
        with open(config.TARGET_FILE, 'r') as f:
            after_lines = f.readlines()

        diff_gen = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f'a/{config.TARGET_FILE}',
            tofile=f'b/{config.TARGET_FILE}',
        )
        return ''.join(diff_gen)
    except Exception as e:
        return f'Error generating diff: {str(e)}'


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SentinelAI - Self-Healing Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/diff2html/bundles/css/diff2html.min.css" />
    <script src="https://cdn.jsdelivr.net/npm/diff2html/bundles/js/diff2html-ui.min.js"></script>

    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 30px; }
        h1 { margin: 0; color: #38bdf8; font-size: 28px; }
        .status-badge { padding: 6px 16px; font-weight: bold; border-radius: 20px; text-transform: uppercase; font-size: 14px; }
        .status-active { background-color: #065f46; color: #34d399; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background-color: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .card-title { font-size: 12px; text-transform: uppercase; color: #94a3b8; font-weight: 600; margin-bottom: 8px; }
        .card-value { font-size: 24px; font-weight: bold; color: #f8fafc; }
        .section-title { font-size: 20px; color: #38bdf8; margin-bottom: 15px; border-left: 4px solid #38bdf8; padding-left: 10px; margin-top: 30px; }
        
        .interactive-box { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        .form-label { display: block; font-size: 13px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }
        .code-textarea, .log-input { width: 100%; box-sizing: border-box; background-color: #090d16; border: 1px solid #334155; color: #38bdf8; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; padding: 12px; border-radius: 6px; }
        .code-textarea { height: 160px; resize: vertical; }
        .btn-submit { background-color: #0284c7; color: white; border: none; padding: 10px 20px; font-weight: bold; font-size: 14px; border-radius: 6px; cursor: pointer; transition: background-color 0.2s; }
        .btn-submit:hover { background-color: #0369a1; }
        .btn-submit:disabled { background-color: #475569; cursor: not-allowed; }

        table { width: 100%; border-collapse: collapse; background-color: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; margin-bottom: 30px; }
        th, td { padding: 14px 20px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #94a3b8; font-size: 13px; text-transform: uppercase; font-weight: 600; }
        tr:last-child td { border-bottom: none; }
        .badge-success { background-color: #14532d; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-fail { background-color: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .log-box { background-color: #090d16; border: 1px solid #334155; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; padding: 15px; border-radius: 8px; height: 180px; overflow-y: auto; color: #a7f3d0; line-height: 1.6; }
        .diff-container-box { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; margin-bottom: 30px; overflow-x: auto; }
        .no-diff-msg { text-align: center; color: #64748b; padding: 30px; font-style: italic; }

        .d2h-wrapper { background-color: #0f172a !important; color: #e2e8f0 !important; border: none !important; }
        .d2h-file-wrapper { border: 1px solid #334155 !important; margin-bottom: 0 !important; background-color: #0f172a !important; }
        .d2h-file-header { background-color: #1e293b !important; border-bottom: 1px solid #334155 !important; }
        .d2h-file-name, .d2h-file-name-wrapper { color: #38bdf8 !important; }
        .d2h-code-wrapper, .d2h-diff-table, .d2h-diff-tbody, .d2h-diff-tr { background-color: #0f172a !important; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important; }
        
        .d2h-code-line, .d2h-code-side-line, .d2h-code-side-emptyplaceholder, .d2h-code-line-ctn, .d2h-cntx, td.d2h-code-side-emptyplaceholder, td.d2h-cntx, td.d2h-info { 
            background-color: #0f172a !important; color: #e2e8f0 !important; border-color: #1e293b !important; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important; 
        }
        .d2h-cntx .d2h-code-line-ctn { color: #94a3b8 !important; }
        .d2h-del, td.d2h-del { background-color: #450a0a !important; color: #fca5a5 !important; border-color: #7f1d1d !important; }
        .d2h-ins, td.d2h-ins { background-color: #052e16 !important; color: #86efac !important; border-color: #14532d !important; }
        .d2h-code-line-prefix, .d2h-code-side-linenumber, td.d2h-code-side-linenumber { color: #64748b !important; background-color: #0f172a !important; border-color: #1e293b !important; }
        .d2h-info { background-color: #1e293b !important; color: #38bdf8 !important; border-color: #334155 !important; }
        .d2h-tag { background-color: #334155 !important; color: #e2e8f0 !important; border-color: #475569 !important; }
    </style>
    <script>
        let lastDiffString = "";

        function renderDiff(diffString) {
            const targetElement = document.getElementById('diff-visualizer');
            targetElement.innerHTML = ''; 
            
            const configuration = {
                drawFileList: false,
                matching: 'lines',
                outputFormat: 'side-by-side',
                highlight: true
            };
            
            const diff2htmlUi = new Diff2HtmlUI(targetElement, diffString, configuration);
            diff2htmlUi.draw();
        }

        function updateMetrics() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-heals').innerText = data.total_incidents;
                    document.getElementById('success-rate').innerText = data.success_rate + '%';
                    document.getElementById('target-file').innerText = data.target;
                    document.getElementById('model-name').innerText = data.model;
                    
                    let tbody = document.getElementById('audit-rows');
                    tbody.innerHTML = '';
                    if (data.history.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #64748b;">Awaiting active system incidents...</td></tr>';
                    } else {
                        [...data.history].reverse().forEach(row => {
                            let statusColor = row.post_fix_verified === 'SUCCESS' ? 'badge-success' : 'badge-fail';
                            let tr = document.createElement('tr');
                            tr.innerHTML = `<td>${new Date(row.timestamp).toLocaleTimeString()}</td><td>${row.error_type}</td><td>${row.action_taken}</td><td><span class="${statusColor}">${row.post_fix_verified}</span></td>`;
                            tbody.appendChild(tr);
                        });
                    }

                    let logBox = document.getElementById('log-lines');
                    logBox.innerHTML = data.recent_logs.join('<br>');
                    logBox.scrollTop = logBox.scrollHeight;

                    if (data.latest_diff && data.latest_diff !== lastDiffString && !window.interactiveDiffActive) {
                        lastDiffString = data.latest_diff;
                        renderDiff(data.latest_diff);
                    } else if (!data.latest_diff && !window.interactiveDiffActive) {
                        document.getElementById('diff-visualizer').innerHTML = '<div class="no-diff-msg">No autonomous patches deployed yet. System running on baseline code.</div>';
                    }
                })
                .catch(err => console.error("Metrics fetch failed:", err));
        }

        function submitInteractiveRemediation() {
            const btn = document.getElementById('btn-remediate');
            const codePayload = document.getElementById('user-code').value;
            const logPayload = document.getElementById('user-log').value;

            if (!codePayload.trim()) {
                alert("Please enter broken Python code to remediate.");
                return;
            }

            btn.disabled = true;
            btn.innerText = "Analyzing & Generating Patch...";

            fetch('/api/remediate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: codePayload, error_log: logPayload })
            })
            .then(res => res.json())
            .then(data => {
                btn.disabled = false;
                btn.innerText = "Analyze & Remediate Patch";

                if (data.status === 'success' && data.diff) {
                    window.interactiveDiffActive = true;
                    renderDiff(data.diff);
                } else {
                    alert("Patching Error: " + (data.message || "Unable to generate patch."));
                }
            })
            .catch(err => {
                btn.disabled = false;
                btn.innerText = "Analyze & Remediate Patch";
                console.error("Remediation request failed:", err);
            });
        }

        setInterval(updateMetrics, 2000);
        window.onload = updateMetrics;
    </script>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>SentinelAI Autonomous Dashboard</h1>
                <div style="color: #64748b; margin-top: 5px;">Self-Healing Site Reliability System Monitoring Platform</div>
            </div>
            <div>
                <span class="status-badge status-active">Orchestrator Online</span>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Target Workload</div>
                <div class="card-value" id="target-file">{{ target }}</div>
            </div>
            <div class="card">
                <div class="card-title">Active AI Model</div>
                <div class="card-value" id="model-name" style="font-size: 18px; margin-top: 6px;">{{ model }}</div>
            </div>
            <div class="card">
                <div class="card-title">Total Intercepted Incidents</div>
                <div class="card-value" id="total-heals">0</div>
            </div>
            <div class="card">
                <div class="card-title">Recovery Success Rate</div>
                <div class="card-value" id="success-rate">0%</div>
            </div>
        </div>

        <div class="section-title">Interactive Remediation Workbench (Dynamic Ingestion)</div>
        <div class="interactive-box">
            <div class="form-group">
                <label class="form-label" for="user-code">Broken Code Snippet</label>
                <textarea id="user-code" class="code-textarea" placeholder="Paste python code with errors here..."></textarea>
            </div>
            <div class="form-group">
                <label class="form-label" for="user-log">Exception / Stack Trace Log (Optional)</label>
                <input type="text" id="user-log" class="log-input" placeholder="e.g., ZeroDivisionError: division by zero" />
            </div>
            <button id="btn-remediate" class="btn-submit" onclick="submitInteractiveRemediation()">Analyze & Remediate Patch</button>
        </div>

        <div class="section-title">Latest AI Patch Diff (Side-by-Side Visualizer)</div>
        <div class="diff-container-box">
            <div id="diff-visualizer">
                <div class="no-diff-msg">Awaiting autonomous patch deployment...</div>
            </div>
        </div>

        <div class="section-title">Remediation Audit Log Trail</div>
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Intercepted Exception Signature</th>
                    <th>Mitigation Deployed</th>
                    <th>Verification Status</th>
                </tr>
            </thead>
            <tbody id="audit-rows">
                <tr><td colspan="4" style="text-align: center; color: #64748b;">Awaiting active system incidents...</td></tr>
            </tbody>
        </table>

        <div class="section-title">Live System Output Tail</div>
        <div class="log-box" id="log-lines">Awaiting telemetry streams...</div>
    </div>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE, target=config.TARGET_FILE, model=config.OPENAI_MODEL
    )


@app.route('/api/metrics')
def api_metrics():
    history = []
    if os.path.exists(config.AUDIT_FILE):
        try:
            with open(config.AUDIT_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass

    total = len(history)
    successes = sum(
        1 for item in history if item.get('post_fix_verified') == 'SUCCESS'
    )
    rate = round((successes / total) * 100) if total > 0 else 0

    recent_logs = []
    if os.path.exists(config.LOG_FILE):
        with open(config.LOG_FILE, 'r') as f:
            recent_logs = f.readlines()[-10:]
            recent_logs = [line.strip() for line in recent_logs]

    latest_diff = get_latest_patch_diff()

    return jsonify({
        'total_incidents': total,
        'success_rate': rate,
        'target': config.TARGET_FILE,
        'model': config.OPENAI_MODEL,
        'history': history,
        'recent_logs': recent_logs,
        'latest_diff': latest_diff,
    })


@app.route('/api/remediate', methods=['POST'])
def api_remediate():
    if analyze_system_error is None:
        return jsonify({'status': 'error', 'message': 'ai_agent.py module unavailable.'}), 500

    data = request.get_json() or {}
    user_code = data.get('code', '')
    error_log = data.get('error_log', 'User Submitted Interactive Incident')

    if not user_code.strip():
        return jsonify({'status': 'error', 'message': 'No code provided'}), 400

    payload = {
        "log": {
            "event_name": "INTERACTIVE_UI_REMEDIATION",
            "message": error_log,
            "timestamp": "NOW"
        },
        "source_code": user_code
    }

    try:
        patched_code = analyze_system_error(payload)

        if not patched_code or patched_code.startswith("AI Analysis failed"):
            return jsonify({'status': 'error', 'message': patched_code or 'Failed to generate patch.'}), 500

        before_lines = user_code.splitlines(keepends=True)
        after_lines = patched_code.splitlines(keepends=True)

        diff_gen = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile='a/user_submission.py',
            tofile='b/user_submission.py',
        )
        diff_string = ''.join(diff_gen)

        return jsonify({
            'status': 'success',
            'patched_code': patched_code,
            'diff': diff_string
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)