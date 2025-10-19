from flask_socketio import SocketIO, emit

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': 'Connected to the server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def send_data(data):
    socketio.emit('update', {'data': data})