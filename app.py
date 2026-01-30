# app.py - FB COOKIE + TOKEN CHECKER WEB PANEL (DEPLOY READY)
from flask import Flask, request, render_template_string, jsonify
import requests, random, re, threading, os
from datetime import datetime

app = Flask(__name__)

ua = [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>⚡ FB COOKIE + TOKEN CHECKER 2025</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {font-family: 'Courier New'; background:#000; color:#0f0; padding:20px; margin:0;}
        textarea {width:100%; height:250px; background:#111; color:#0f0; border:2px solid #0f0; border-radius:10px; padding:15px; font-size:16px;}
        button {width:100%; padding:20px; background:#0f0; color:#000; border:none; border-radius:10px; font-size:20px; font-weight:bold; margin:10px 0; cursor:pointer;}
        .result {background:#111; border:2px solid #0f0; padding:15px; height:400px; overflow-y:scroll; margin-top:20px; border-radius:10px;}
        .live {color:#0f0;} .die {color:#f00;} .cp {color:#ff0;}
        h1 {text-align:center; text-shadow: 0 0 10px #0f0;}
    </style>
</head>
<body>
    <h1>⚡ FB COOKIE + TOKEN CHECKER PRO ⚡</h1>
    <p style="text-align:center;">Paste Cookies or Tokens (1 per line)</p>
    <textarea id="cookies" placeholder="c_user=1000...; xs=28:...&#10;EAAAAU..."></textarea>
    <button onclick="checkAll()">🚀 START CHECKING</button>
    <button onclick="document.getElementById('result').innerHTML=''">🗑️ CLEAR RESULTS</button>
    <div id="result" class="result"></div>

    <script>
    function checkAll() {
        let cookies = document.getElementById('cookies').value.trim().split('\\n');
        let result = document.getElementById('result');
        result.innerHTML = '<div style="color:#0f0">🔥 Starting checker...</div>';
        
        let count = 0;
        cookies.forEach(line => {
            if (!line.trim()) return;
            fetch('/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({entry: line.trim()})
            })
            .then(r => r.json())
            .then(data => {
                count++;
                let color = data.status.includes('LIVE') ? '#0f0' : data.status.includes('CHECKPOINT') ? '#ff0' : '#f00';
                result.innerHTML += `<div style="color:${color}">[${count}] ${data.message}</div>`;
                result.scrollTop = result.scrollHeight;
            });
        });
    }
    </script>
</body>
</html>
"""

def check_entry(entry):
    headers = {"User-Agent": random.choice(ua)}
    token = None

    if entry.startswith("EAA"):
        token = entry
    else:
        try:
            cookies_dict = dict([c.split("=",1) for c in entry.split("; ") if "=" in c])
            r = requests.get("https://business.facebook.com/business_locations", headers=headers, cookies=cookies_dict, timeout=15)
            token_match = re.search(r'EAA[0-9A-Za-z]+', r.text)
            if token_match: token = token_match.group(0)
        except: pass

    if not token:
        return {"status": "DIE", "message": "❌ No Token Found"}

    try:
        r = requests.get(f"https://graph.facebook.com/v18.0/me?access_token={token}&fields=name,id,friends.limit(0).summary(true)", headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            name = data.get("name", "Unknown")
            uid = data.get("id")
            friends = data.get("friends", {}).get("summary", {}).get("total_count", 0)
            return {"status": "LIVE", "message": f"✅ LIVE → {name} | {uid} | Friends: {friends}"}
        else:
            err = r.json().get("error", {}).get("message", "")
            if "checkpoint" in err.lower() or "requires" in err.lower():
                return {"status": "CHECKPOINT", "message": f"🔒 CHECKPOINT/2FA → {err[:60]}"}
            elif "expired" in err.lower():
                return {"status": "DIE", "message": f"💀 EXPIRED → {err[:60]}"}
            else:
                return {"status": "LIMITED", "message": f"🚫 LIMITED → {err[:60]}"}
    except:
        return {"status": "ERROR", "message": "🌐 Connection Error"}

@app.route('/')
def home():
    return HTML

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    entry = data.get('entry', '')
    result = check_entry(entry)
    return jsonify(result)

# Auto clear old results on restart
if os.path.exists("live_cookies_tokens.txt"):
    open("live_cookies_tokens.txt", "w").close()

print("🚀 FB CHECKER IS RUNNING - GO TO YOUR LINK!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
