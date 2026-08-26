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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

        :root {
            --bg: #f3efe7;
            --panel: #f9f7f3;
            --surface: #ffffff;
            --surface-strong: #edf3f1;
            --border: #dfe5df;
            --primary: #123f43;
            --primary-soft: #dfeeea;
            --accent: #4d8a71;
            --accent-strong: #2f6b56;
            --text: #182426;
            --muted: #5d6d6f;
            --shadow: rgba(18, 63, 67, 0.12);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: linear-gradient(180deg, #f7f4ee 0%, #eef3f0 100%);
            color: var(--text);
            font-family: 'Inter', sans-serif;
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
            background: var(--primary);
            color: #edf8f4;
            border-bottom: 1px solid rgba(255,255,255,0.16);
            padding: 0.6rem 1rem;
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .container {
            width: 100%;
            max-width: 640px;
            margin-top: 2.5rem;
        }

        .header {
            margin-bottom: 2rem;
        }

        .badge {
            display: inline-block;
            background: var(--primary-soft);
            border: 1px solid rgba(18, 63, 67, 0.18);
            color: var(--primary);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            padding: 0.4rem 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: clamp(2rem, 4vw, 2.6rem);
            font-weight: 800;
            letter-spacing: -0.05em;
            line-height: 1.05;
            margin-bottom: 0.85rem;
            color: var(--text);
        }

        .subtitle {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.7;
            max-width: 540px;
        }

        .form-card {
            background: rgba(255,255,255,0.9);
            border: 1px solid var(--border);
            box-shadow: 0 12px 35px var(--shadow);
            padding: 2rem;
            border-radius: 18px;
        }

        .field {
            margin-bottom: 1.4rem;
        }

        label {
            display: block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: var(--primary);
            letter-spacing: 0.08em;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }

        input, select, textarea {
            width: 100%;
            background: var(--panel);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            font-size: 0.97rem;
            padding: 0.85rem 0.95rem;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        input:focus, select:focus, textarea:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(77, 138, 113, 0.08);
        }

        textarea {
            resize: vertical;
            min-height: 130px;
        }

        select option { background: var(--surface); }

        .submit-btn {
            width: 100%;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent-strong) 100%);
            color: #f3faf6;
            border: none;
            padding: 1rem 1.1rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.15s ease, opacity 0.2s ease;
        }

        .submit-btn:hover {
            opacity: 0.96;
            transform: translateY(-1px);
        }

        .security-note {
            margin-top: 1.5rem;
            padding: 1rem 1rem 0.8rem;
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            background: var(--surface-strong);
            font-size: 0.76rem;
            color: var(--muted);
            font-family: 'IBM Plex Mono', monospace;
            line-height: 1.7;
            border-radius: 12px;
        }

        .success {
            display: none;
            background: var(--primary-soft);
            border: 1px solid rgba(18, 63, 67, 0.18);
            border-radius: 12px;
            padding: 1.4rem;
            text-align: center;
            margin-top: 1rem;
        }

        .success .id {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.2rem;
            color: var(--primary);
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
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }

        .stat-num {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.4rem;
            color: var(--primary);
            margin-bottom: 0.2rem;
        }

        .stat-label {
            font-size: 0.72rem;
            color: var(--muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="warning-bar">
        Confidential reporting channel · demo only
    </div>

    <div class="container">
        <div class="header">
            <div class="badge">Safe reporting · confidential · protected</div>
            <h1>Secure reporting<br>for affected communities</h1>
            <p class="subtitle">
                Share credible information anonymously and without exposing your identity.
                This channel is designed for sensitive reporting in high-risk environments.
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
