from flask import Flask, render_template
from flask_socketio import SocketIO
from config import Config
from services.suricata_client import SuricataClient
from sockets import setup_sockets
import os

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

# get Suricata URL from app config or environment, fallback to localhost
suricata_url = app.config.get('SURICATA_URL') or os.environ.get('SURICATA_URL') or 'http://127.0.0.1:8000'
suricata_client = SuricataClient(suricata_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    setup_sockets(socketio, suricata_client)
    socketio.run(app, host='0.0.0.0', port=5000)