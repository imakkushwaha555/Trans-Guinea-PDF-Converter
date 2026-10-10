import os
import sys
import threading
import webbrowser
from pathlib import Path

APP_TITLE = "Trans-Guinea PDF Converter"


def _redirect_streams_if_windowed() -> None:
    # Windowed builds have no console, so stdout/stderr are None.
    if sys.stdout is not None and sys.stderr is not None:
        return
    if sys.platform == "darwin":
        log_dir = Path.home() / "Library" / "Logs" / APP_TITLE
    else:
        log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_TITLE
    log_dir.mkdir(parents=True, exist_ok=True)
    log = open(log_dir / "app.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or log
    sys.stderr = sys.stderr or log


def _open_native_window(url: str) -> bool:
    try:
        import webview
    except Exception as error:
        print(f"Native window unavailable ({error}); falling back to the browser.")
        return False
    try:
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.create_window(APP_TITLE, url, width=1180, height=860, min_size=(760, 600))
        webview.start()
        return True
    except Exception as error:
        print(f"Native window failed ({error}); falling back to the browser.")
        return False


def main() -> None:
    _redirect_streams_if_windowed()
    from werkzeug.serving import make_server

    from app import app

    # The server only listens on this machine, on a free port chosen for this run.
    server = make_server("127.0.0.1", 0, app, threaded=True)
    url = f"http://127.0.0.1:{server.server_port}"
    threading.Thread(target=server.serve_forever, daemon=True).start()

    if "--browser" in sys.argv or not _open_native_window(url):
        # Browser mode: the app stays alive until this process is stopped.
        webbrowser.open(url)
        threading.Event().wait()
    server.shutdown()


if __name__ == "__main__":
    main()
