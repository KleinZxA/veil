import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    SURICATA_API_URL = os.environ.get('SURICATA_API_URL') or 'http://localhost:3000'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or 'redis://localhost:6379/0'