from flask_socketio import send, emit


def init_socket_tio_handlers(socket_io):
    @socket_io.on('message')
    def handle_message(message):
        print('received message on handle message: ' + message)
        return message

    @socket_io.on('json')
    def handle_json(json):
        print('received json on handle json: ' + str(json))
        return json

    @socket_io.on('dashboard connected')
    def dashboard_connected(json):
        print('dashboard connected: ' + str(json))

    @socket_io.on('refresh dashboard')
    def refresh_dashboard(json):
        print('Refresh dashboard: ' + str(json))
        emit('refresh dashboard', json, json=True)

