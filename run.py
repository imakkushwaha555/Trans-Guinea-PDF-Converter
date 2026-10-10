import socket
import threading
import webbrowser

from app import app


def main() -> None:
    with socket.socket() as socket_handle:
        socket_handle.bind(("127.0.0.1", 0))
        port = socket_handle.getsockname()[1]

    threading.Timer(0.8, webbrowser.open, args=(f"http://127.0.0.1:{port}",)).start()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()