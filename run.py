"""
Start FinSync locally:   python run.py
Then open http://127.0.0.1:5000 in your browser.
"""
# Load the tools needed in this file.
import os

# Use functions and classes from another file.
from app import create_app

# Set up the Flask application or its routes.
app = create_app()

# Check the condition before continuing.
if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(host="127.0.0.1", port=5000, debug=debug)
