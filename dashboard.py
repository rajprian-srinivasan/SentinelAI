import os
import json
from flask import Flask, render_template_string, jsonify
import config

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SentinelAI - Self-Healing Dashboard</title>
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
        .section-title { font-size: 20px; color: #38bdf8; margin-bottom: 15px; border-left: 4px solid #38bdf8; padding-left: 10px; }
        table { width: 100%; border-collapse: collapse; background-color: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; margin-bottom: 30px; }
        th, td { padding: 14px 20px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #94a3b8; font-size: 13px; text-transform: uppercase; font-weight: 600; }
        tr:last-child td { border-bottom: none; }
        .badge-success { background-color: #14532d; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-fail { background-color: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .log-box { background-color: #090d16; border: 1px solid #334155; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; padding: 15px; border-radius: 8px; height: 200px; overflow-y: auto; color: #a7f3d0; line-height: 1.6; }
    </style>
    <script>
        setInterval(function() {
            fetch('/api/metrics').then(response => response.json()).then(data => {
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
            });
        }, 2000);
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

    return jsonify({
        "total_incidents": total,
        "success_rate": rate,
        "target": config.TARGET_FILE,
        "model": config.OPENAI_MODEL,
        "history": history,
        "recent_logs": recent_logs
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)