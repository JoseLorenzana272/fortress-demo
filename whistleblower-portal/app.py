from flask import Flask, request, jsonify, render_template_string
import uuid
import datetime

app = Flask(__name__)

# In-memory storage (demo only - no real DB needed)
submissions = []

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Whistleblower Portal</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

        :root {
            --bg: #0a0a0f;
            --surface: #111118;
            --border: #1e1e2e;
            --accent: #00ff88;
            --accent-dim: rgba(0,255,136,0.1);
            --text: #e0e0e0;
            --muted: #666;
            --danger: #ff4444;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'IBM Plex Sans', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .warning-bar {
            position: fixed;
            top: 0; left: 0; right: 0;
            background: var(--accent-dim);
            border-bottom: 1px solid var(--accent);
            padding: 0.5rem 1rem;
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            color: var(--accent);
            letter-spacing: 0.05em;
        }

        .container {
            width: 100%;
            max-width: 580px;
            margin-top: 2rem;
        }

        .header {
            margin-bottom: 2.5rem;
        }

        .badge {
            display: inline-block;
            background: var(--accent-dim);
            border: 1px solid var(--accent);
            color: var(--accent);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            padding: 0.25rem 0.75rem;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-bottom: 0.75rem;
        }

        .subtitle {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .form-card {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 2rem;
        }

        .field {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            color: var(--accent);
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }

        input, select, textarea {
            width: 100%;
            background: var(--bg);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.9rem;
            padding: 0.75rem 1rem;
            outline: none;
            transition: border-color 0.2s;
        }

        input:focus, select:focus, textarea:focus {
            border-color: var(--accent);
        }

        textarea {
            resize: vertical;
            min-height: 120px;
        }

        select option { background: var(--surface); }

        .submit-btn {
            width: 100%;
            background: var(--accent);
            color: #000;
            border: none;
            padding: 1rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        .submit-btn:hover { opacity: 0.85; }

        .security-note {
            margin-top: 1.5rem;
            padding: 1rem;
            border: 1px solid var(--border);
            font-size: 0.8rem;
            color: var(--muted);
            font-family: 'IBM Plex Mono', monospace;
            line-height: 1.6;
        }

        .success {
            display: none;
            background: var(--accent-dim);
            border: 1px solid var(--accent);
            padding: 1.5rem;
            text-align: center;
            margin-top: 1rem;
        }

        .success .id {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.2rem;
            color: var(--accent);
            margin: 0.5rem 0;
        }

        .stats {
            margin-top: 1.5rem;
            display: flex;
            gap: 1rem;
        }

        .stat {
            flex: 1;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1rem;
            text-align: center;
        }

        .stat-num {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.5rem;
            color: var(--accent);
        }

        .stat-label {
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 0.25rem;
        }
    </style>
</head>
<body>
    <div class="warning-bar">
        ⚠ THIS IS A DEMO — DO NOT SUBMIT REAL SENSITIVE INFORMATION
    </div>

    <div class="container">
        <div class="header">
            <div class="badge">ENCRYPTED · ANONYMOUS · SECURE</div>
            <h1>Whistleblower<br>Secure Portal</h1>
            <p class="subtitle">
                Submit tips anonymously. Your identity is never stored.
                All submissions are encrypted in transit.
            </p>
        </div>

        <div class="form-card">
            <form id="tipForm">
                <div class="field">
                    <label>CATEGORY</label>
                    <select name="category" required>
                        <option value="">Select a category...</option>
                        <option value="corruption">Government Corruption</option>
                        <option value="human_rights">Human Rights Violation</option>
                        <option value="environmental">Environmental Crime</option>
                        <option value="financial">Financial Fraud</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <div class="field">
                    <label>URGENCY LEVEL</label>
                    <select name="urgency" required>
                        <option value="">Select urgency...</option>
                        <option value="critical">Critical — Imminent danger</option>
                        <option value="high">High — Within days</option>
                        <option value="medium">Medium — Within weeks</option>
                        <option value="low">Low — For the record</option>
                    </select>
                </div>

                <div class="field">
                    <label>YOUR INFORMATION (OPTIONAL — NEVER STORED)</label>
                    <input type="text" name="contact" placeholder="Secure contact method (optional)">
                </div>

                <div class="field">
                    <label>DESCRIPTION</label>
                    <textarea name="description" placeholder="Describe what you witnessed. Be as specific as possible — dates, locations, names, organizations involved." required></textarea>
                </div>

                <button type="submit" class="submit-btn">SUBMIT ANONYMOUS TIP →</button>
            </form>

            <div class="success" id="successMsg">
                <div style="color: var(--accent); font-size: 1.5rem; margin-bottom: 0.5rem;">✓</div>
                <div style="font-weight: 600;">Tip Submitted Successfully</div>
                <div class="id" id="submissionId"></div>
                <div style="font-size: 0.8rem; color: var(--muted); margin-top: 0.5rem;">
                    Save this ID to follow up on your submission
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-num" id="totalCount">{{ total }}</div>
                <div class="stat-label">TIPS RECEIVED</div>
            </div>
            <div class="stat">
                <div class="stat-num">256-bit</div>
                <div class="stat-label">ENCRYPTION</div>
            </div>
            <div class="stat">
                <div class="stat-num">0</div>
                <div class="stat-label">IDs STORED</div>
            </div>
        </div>

        <div class="security-note">
            // SECURITY: This portal runs inside Fortress in a Box.<br>
            // Runtime monitored by Falco. Policies enforced by Kyverno.<br>
            // Any unauthorized shell access triggers immediate alerts.
        </div>
    </div>

    <script>
        document.getElementById('tipForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const data = Object.fromEntries(new FormData(form));

            const res = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();
            document.getElementById('submissionId').textContent = '#' + result.id;
            document.getElementById('successMsg').style.display = 'block';
            document.getElementById('totalCount').textContent = result.total;
            form.reset();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, total=len(submissions))

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    submission = {
        'id': str(uuid.uuid4())[:8].upper(),
        'category': data.get('category'),
        'urgency': data.get('urgency'),
        'description': data.get('description'),
        'timestamp': datetime.datetime.utcnow().isoformat()
        # contact is intentionally NOT stored
    }
    submissions.append(submission)
    return jsonify({'id': submission['id'], 'total': len(submissions)})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
