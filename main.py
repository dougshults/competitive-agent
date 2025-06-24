"""
PropTech Intel Flask Application - Replit Deployment Entry Point
This file serves as the main entry point for running the Flask app on Replit.
"""

from app import app

# This ensures Gunicorn can find the app instance
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
