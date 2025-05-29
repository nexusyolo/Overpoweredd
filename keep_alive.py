from flask import Flask
import threading
import time

app = Flask('')

@app.route('/')
def home():
    return f"Bot is running! Timestamp: {int(time.time())}"

@app.route('/health')
def health():
    return {"status": "alive", "timestamp": int(time.time())}

def run():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def keep_alive():
    t = threading.Thread(target=run, daemon=True)
    t.start()