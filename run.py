import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

def _redirect_streams_if_windowed() -> None:
    # Windowed builds have no console, so stdout/stderr are None.
    if sys.stdout is not None and sys.stderr is not None:
        return
    if sys.platform == "darwin":
        log_dir = Path.home() / "Library" / "Logs" / "Trans-Guinea PDF Converter"
    else:
        log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Trans-Guinea PDF Converter"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = open(log_dir / "app.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or log
    sys.stderr = sys.stderr or log


def main() -> None:
    _redirect_streams_if_windowed()
    from app import app

    with socket.socket() as socket_handle:
        socket_handle.bind(("127.0.0.1", 0))
        port = socket_handle.getsockname()[1]

    threading.Timer(0.8, webbrowser.open, args=(f"http://127.0.0.1:{port}",)).start()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()