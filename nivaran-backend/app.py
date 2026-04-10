"""
NIVARAN — AI-Powered Civic & Legal Companion for Digital Inclusion
Flask Application Entry Point

Initializes Flask, Flask-SocketIO, CORS, and registers route blueprints.
"""

import os
import sqlite3
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# ───────────────────────────────────────────────────────
# App Initialization
# ───────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nivaran-dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Temporary audio directory (served to frontend, cleaned periodically)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'temp_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# ───────────────────────────────────────────────────────
# CORS — Allow React dev server on port 3000
# ───────────────────────────────────────────────────────
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]},
    r"/audio/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]},
})

# ───────────────────────────────────────────────────────
# Flask-SocketIO — Real-time progress streaming
# ───────────────────────────────────────────────────────
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    logger=False,
    engineio_logger=False
)

# ───────────────────────────────────────────────────────
# Database Initialization
# ───────────────────────────────────────────────────────
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'rules.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'rules', 'schema.sql')


def init_database():
    """Initialize SQLite database from schema.sql if rules.db does not exist."""
    db_dir = os.path.dirname(DATABASE_PATH)
    os.makedirs(db_dir, exist_ok=True)

    if not os.path.exists(DATABASE_PATH) or os.path.getsize(DATABASE_PATH) == 0:
        print("[NIVARAN] Initializing database from schema.sql...")
        conn = sqlite3.connect(DATABASE_PATH)
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("[NIVARAN] Database initialized successfully.")
    else:
        print("[NIVARAN] Database already exists, skipping initialization.")


# ───────────────────────────────────────────────────────
# Register Route Blueprints
# ───────────────────────────────────────────────────────
from routes.civic_ease import civic_ease_bp
from routes.rent_right import rent_right_bp
from routes.demo_route import demo_bp

app.register_blueprint(civic_ease_bp, url_prefix='/api/civic-ease')
app.register_blueprint(rent_right_bp, url_prefix='/api/rent-right')
app.register_blueprint(demo_bp, url_prefix='/api/demo')


# ───────────────────────────────────────────────────────
# Static Audio File Serving
# ───────────────────────────────────────────────────────
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files from the temp_audio directory."""
    return send_from_directory(AUDIO_DIR, filename, mimetype='audio/mpeg')


# ───────────────────────────────────────────────────────
# Health Check Endpoint
# ───────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        'status': 'healthy',
        'service': 'NIVARAN Backend',
        'version': '1.0.0',
        'modules': ['civic-ease', 'rent-right']
    }, 200


# ───────────────────────────────────────────────────────
# Debug Endpoint (TEMPORARY — for API key diagnosis)
# ───────────────────────────────────────────────────────
@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Temporary endpoint to verify API key is loaded."""
    from dotenv import load_dotenv, find_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path, override=True)
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or 'NOT FOUND'
    env_exists = os.path.exists(env_path)
    return {
        'key_found': key != 'NOT FOUND' and not key.startswith('your_'),
        'key_prefix': key[:8] + '...' if key not in ('NOT FOUND',) and not key.startswith('your_') else 'N/A',
        'key_length': len(key) if key != 'NOT FOUND' else 0,
        'env_file_exists': env_exists,
        'env_file_path': env_path,
    }, 200


# ───────────────────────────────────────────────────────
# SocketIO Event Handlers
# ───────────────────────────────────────────────────────
@socketio.on('connect')
def handle_connect():
    print(f"[NIVARAN] Client connected")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"[NIVARAN] Client disconnected")


# ───────────────────────────────────────────────────────
# App Entry Point
# ───────────────────────────────────────────────────────
if __name__ == '__main__':
    init_database()
    print("[NIVARAN] Starting server on http://localhost:5000")
    # allow_unsafe_werkzeug=True is needed for modern Werkzeug + SocketIO in development
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
