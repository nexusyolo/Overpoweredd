from flask import Flask
import os
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    """Runs the Flask app."""
    try:
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
    except Exception as e:
        logging.error(f"Error starting Flask app: {e}")

if __name__ == "__main__":
    run()