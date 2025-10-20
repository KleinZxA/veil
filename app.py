# Monkey-patch must happen before other imports
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import os

# Create Flask app first
app = Flask(__name__)

# Basic config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SURICATA_EVE_PATH = os.environ.get('SURICATA_EVE_PATH') or r"C:\Program Files\Suricata\log\eve.json"

app.config.from_object(Config)

# Initialize SocketIO after app creation
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Import components that need app context
from services.suricata_client import SuricataClient
from sockets import setup_sockets

# Configure Suricata client
eve_path = app.config.get("SURICATA_EVE_PATH")
suricata_client = SuricataClient(eve_path=eve_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Setup sockets with app context
with app.app_context():
    setup_sockets(socketio, suricata_client)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)