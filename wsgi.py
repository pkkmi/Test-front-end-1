"""
WSGI entry point for the application.
This file assists with the proper startup of the application.
"""
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup message
logger.info("WSGI ENTRY POINT - INITIALIZING APPLICATION")

# Import the Flask application
from app import app as application

# Provide an app object for Gunicorn
app = application

# For local testing
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting development server on port {port}")
    app.run(host="0.0.0.0", port=port)
