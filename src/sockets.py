from flask_socketio import SocketIO, emit
import threading
import time
import queue

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
    """
    Register connect/disconnect handlers and start a background thread
    that emits Suricata events to connected Socket.IO clients.

    Expected SuricataClient interfaces (any one of):
      - suricata_client.subscribe(callback)  -> callback(event_dict)
      - suricata_client.events (queue.Queue) -> queue of event_dict
      - suricata_client.stream() -> iterator/generator yielding event_dict
      - suricata_client.get_events() or suricata_client.fetch() -> list of events (polled)
      - optional: suricata_client.start() / suricata_client.stop()
    """
    stop_event = threading.Event()
    worker_thread = {"t": None}  # container to allow assignment from nested funcs

    def emit_event(evt):
        try:
            socketio.emit('suricata_event', evt)
        except Exception:
            # swallow socket errors; thread stays alive
            pass

    def background_loop():
        # Priority: subscribe -> queue -> stream -> polling
        try:
            if hasattr(suricata_client, 'subscribe'):
                # subscribe style: client pushes into our callback
                def cb(evt):
                    emit_event(evt)
                try:
                    suricata_client.subscribe(cb)
                except Exception:
                    # if subscribe blocks, return
                    return
                # keep thread alive until stopped
                while not stop_event.wait(1):
                    time.sleep(0.5)
                return

            if hasattr(suricata_client, 'events') and isinstance(getattr(suricata_client, 'events'), queue.Queue):
                q = suricata_client.events
                while not stop_event.is_set():
                    try:
                        evt = q.get(timeout=1)
                        emit_event(evt)
                    except queue.Empty:
                        continue
                return

            if hasattr(suricata_client, 'stream'):
                try:
                    for evt in suricata_client.stream():
                        if stop_event.is_set():
                            break
                        emit_event(evt)
                except Exception:
                    # fallback to polling below
                    pass

            # Polling fallback
            while not stop_event.is_set():
                evts = []
                try:
                    if hasattr(suricata_client, 'get_events'):
                        evts = suricata_client.get_events()
                    elif hasattr(suricata_client, 'fetch'):
                        evts = suricata_client.fetch()
                except Exception:
                    evts = []
                if evts:
                    for e in evts:
                        emit_event(e)
                # reasonable sleep to avoid tight loop
                time.sleep(1)
        except Exception:
            # ensure thread doesn't crash silently
            while not stop_event.wait(1):
                time.sleep(1)

    def start_background():
        # call client's start() if available
        try:
            if hasattr(suricata_client, 'start'):
                suricata_client.start()
        except Exception:
            pass
        t = threading.Thread(target=background_loop, daemon=True)
        t.start()
        worker_thread["t"] = t
        return t

    # register connect/disconnect handlers
    def on_connect(sid, environ):
        # start worker once when first client connects
        if worker_thread["t"] is None:
            start_background()
        try:
            socketio.emit('status', {'status': 'connected'}, room=sid)
        except Exception:
            pass

    def on_disconnect(sid):
        # stop worker when client disconnects (you can change logic to stop only when no clients remain)
        try:
            if hasattr(suricata_client, 'stop'):
                suricata_client.stop()
        except Exception:
            pass
        stop_event.set()

    # Register events with the provided SocketIO instance
    # Using on_event to avoid decorator scope issues
    socketio.on_event('connect', on_connect)
    socketio.on_event('disconnect', on_disconnect)