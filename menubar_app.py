"""
Menu bar app for Prompt Optimizer.
Run via PromptOptimizer.app or: python3 menubar_app.py
"""

import os
import subprocess
import threading
import webbrowser

import rumps

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8501
URL = f"http://localhost:{PORT}"


class PromptOptimizerApp(rumps.App):
    def __init__(self):
        super().__init__("⚡", quit_button=None)
        self._proc = None

        self.start_item = rumps.MenuItem("Start Server", callback=self.start_server)
        self.stop_item  = rumps.MenuItem("Stop Server",  callback=self.stop_server)
        self.open_item  = rumps.MenuItem("Open in Browser", callback=self.open_browser)

        self.stop_item.set_callback(None)   # disabled until server runs

        self.menu = [
            self.open_item,
            None,
            self.start_item,
            self.stop_item,
            None,
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        # Auto-start on launch
        self._start()

    # ------------------------------------------------------------------ #
    # Server management
    # ------------------------------------------------------------------ #

    def _start(self):
        if self._proc and self._proc.poll() is None:
            return
        self._proc = subprocess.Popen(
            [
                "python3", "-m", "streamlit", "run", "app.py",
                "--server.headless", "true",
                "--server.port", str(PORT),
            ],
            cwd=APP_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._set_state(running=True)
        threading.Timer(2.5, lambda: webbrowser.open(URL)).start()

    def _stop(self):
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
        self._set_state(running=False)

    def _set_state(self, running: bool):
        self.title = "⚡" if running else "⚡ ●"
        self.start_item.set_callback(None if running else self.start_server)
        self.stop_item.set_callback(self.stop_server if running else None)

    # ------------------------------------------------------------------ #
    # Menu callbacks
    # ------------------------------------------------------------------ #

    @rumps.clicked("Start Server")
    def start_server(self, _):
        self._start()

    @rumps.clicked("Stop Server")
    def stop_server(self, _):
        self._stop()

    @rumps.clicked("Open in Browser")
    def open_browser(self, _):
        webbrowser.open(URL)

    def quit_app(self, _):
        self._stop()
        rumps.quit_application()


if __name__ == "__main__":
    PromptOptimizerApp().run()
