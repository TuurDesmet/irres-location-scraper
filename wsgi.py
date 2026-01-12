"""
Wsgi entry point for production deployment
Use with Gunicorn or uWSGI
"""

from api import app

if __name__ == "__main__":
    app.run()
