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

        self.stop_item.set_callback(None)

        self.menu = [
            self.open_item,
            None,
            self.start_item,
            self.stop_item,
            None,
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        self._kill_existing()
        self._start()

    def _kill_existing(self):
        """Kill any stale Streamlit process on our port before starting fresh."""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{PORT}"],
                capture_output=True, text=True
            )
            pids = result.stdout.strip().split()
            for pid in pids:
                subprocess.run(["kill", "-9", pid], capture_output=True)
        except Exception:
            pass

    def _start(self):
        if self._proc and self._proc.poll() is None:
            return
        self._proc = subprocess.Popen(
            [
                "python3", "-m", "streamlit", "run", "app.py",
                "--server.headless", "true",
                "--server.port", str(PORT),
                "--server.fileWatcherType", "none",
            ],
            cwd=APP_DIR,
            stdout=open("/tmp/promptopt.log", "w"),
            stderr=subprocess.STDOUT,
            # Detach from parent so server survives if menubar app restarts
            start_new_session=True,
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
        self._kill_existing()
        self._set_state(running=False)

    def _set_state(self, running: bool):
        self.title = "⚡" if running else "⚡●"
        self.start_item.set_callback(None if running else self.start_server)
        self.stop_item.set_callback(self.stop_server if running else None)

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
