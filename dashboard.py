import os
import json
import glob
import difflib
from flask import Flask, render_template_string, jsonify
import config

app = Flask(__name__)

def get_latest_patch_diff():
    """Reads the latest pre-heal backup file and compares it to current TARGET_FILE."""
    if not os.path.exists("patches"):
        return ""

    patch_files = glob.glob("patches/*_pre_heal_*")
    if not patch_files or not os.path.exists(config.TARGET_FILE):
        return ""

    
    latest_backup = max(patch_files, key=os.path.getmtime)

    try:
        with open(latest_backup, "r") as f:
            before_lines = f.readlines()
        with open(config.TARGET_FILE, "r") as f:
            after_lines = f.readlines()

        diff_gen = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{os.path.basename(latest_backup)}",
            tofile=f"b/{config.TARGET_FILE}",
        )
        return "".join(diff_gen)
    except Exception as e:
        return f"Error generating diff: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SentinelAI - Self-Healing Dashboard</title>
    <!-- Diff2Html CSS & JS via CDN -->
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
        table { width: 100%; border-collapse: collapse; background-color: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; margin-bottom: 30px; }
        th, td { padding: 14px 20px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #94a3b8; font-size: 13px; text-transform: uppercase; font-weight: 600; }
        tr:last-child td { border-bottom: none; }
        .badge-success { background-color: #14532d; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-fail { background-color: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .log-box { background-color: #090d16; border: 1px solid #334155; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; padding: 15px; border-radius: 8px; height: 200px; overflow-y: auto; color: #a7f3d0; line-height: 1.6; }
        .diff-container-box { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; margin-bottom: 30px; overflow-x: auto; }
        .no-diff-msg { text-align: center; color: #64748b; padding: 30px; font-style: italic; }

        /* Dark Mode Theme Overrides for Diff2Html */
        .d2h-wrapper { background-color: #0f172a !important; color: #e2e8f0 !important; border: 1px solid #334155 !important; border-radius: 6px; }
        .d2h-file-header { background-color: #1e293b !important; border-bottom: 1px solid #334155 !important; }
        .d2h-file-name { color: #38bdf8 !important; }
        .d2h-code-line, .d2h-code-side-line { color: #e2e8f0 !important; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important; }
        .d2h-code-line-ctn { color: #e2e8f0 !important; }
        .d2h-del { background-color: #450a0a !important; color: #fca5a5 !important; }
        .d2h-ins { background-color: #052e16 !important; color: #86efac !important; }
        .d2h-code-side-emptyplaceholder { background-color: #0f172a !important; border-color: #334155 !important; }
        .d2h-code-line-prefix { color: #64748b !important; }
        .d2h-info { background-color: #1e293b !important; color: #94a3b8 !important; border-color: #334155 !important; }
    </style>
    <script>
        let lastDiffString = "";

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

                    // Update Side-by-Side Diff Visualizer if a new diff arrives
                    if (data.latest_diff && data.latest_diff !== lastDiffString) {
                        lastDiffString = data.latest_diff;
                        const targetElement = document.getElementById('diff-visualizer');
                        targetElement.innerHTML = ''; // Clear previous diff
                        
                        const configuration = {
                            drawFileList: false,
                            matching: 'lines',
                            outputFormat: 'side-by-side',
                            highlight: true
                        };
                        
                        const diff2htmlUi = new Diff2HtmlUI(targetElement, data.latest_diff, configuration);
                        diff2htmlUi.draw();
                    } else if (!data.latest_diff) {
                        document.getElementById('diff-visualizer').innerHTML = '<div class="no-diff-msg">No autonomous patches deployed yet. System running on baseline code.</div>';
                    }
                })
                .catch(err => console.error("Metrics fetch failed:", err));
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
    return render_template_string(HTML_TEMPLATE, target=config.TARGET_FILE, model=config.OPENAI_MODEL)

@app.route('/api/metrics')
def api_metrics():
    history = []
    if os.path.exists(config.AUDIT_FILE):
        try:
            with open(config.AUDIT_FILE, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
            
    total = len(history)
    successes = sum(1 for item in history if item.get("post_fix_verified") == "SUCCESS")
    rate = round((successes / total) * 100) if total > 0 else 0
    
    recent_logs = []
    if os.path.exists(config.LOG_FILE):
        with open(config.LOG_FILE, "r") as f:
            recent_logs = f.readlines()[-10:]
            recent_logs = [line.strip() for line in recent_logs]

    latest_diff = get_latest_patch_diff()

    return jsonify({
        "total_incidents": total,
        "success_rate": rate,
        "target": config.TARGET_FILE,
        "model": config.OPENAI_MODEL,
        "history": history,
        "recent_logs": recent_logs,
        "latest_diff": latest_diff
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)