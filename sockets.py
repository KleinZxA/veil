from flask_socketio import SocketIO, emit
import threading
import time

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': 'Connected to the server!'})
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def send_data(data):
    socketio.emit('update', {'data': data})

def setup_sockets(socketio, suricata_client):
    """Setup Socket.IO event handlers and start Suricata event stream."""
    import threading
    
    def event_emitter():
        """Background thread that reads from Suricata and emits events."""
        print("Starting Suricata event stream...")
        try:
            for event in suricata_client.stream():
                try:
                    print("Emitting event:", event)  # Debug print
                    socketio.emit('suricata_event', event)
                except Exception as e:
                    print(f"Error emitting event: {e}")
        except Exception as e:
            print(f"Error in event stream: {e}")

    thread = threading.Thread(target=event_emitter, daemon=True)
    thread.start()

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection without sid/environ arguments."""
        print("Client connected")
        socketio.emit('status', {'connected': True})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print("Client disconnected")