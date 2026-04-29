import subprocess
import time

class AudioController:
    def __init__(self, file_path, debug=False):
        self.file_path = file_path
        self.debug = debug
        self.process = None
        self.start_time = None

    def start(self):
        """Starts mpv (fallback to ffplay) in no-video mode."""
        stderr = None if self.debug else subprocess.DEVNULL
        try:
            self.process = subprocess.Popen(
                ["mpv", "--no-video", "--really-quiet", self.file_path],
                stdout=subprocess.DEVNULL,
                stderr=stderr
            )
        except FileNotFoundError:
            # Fallback to ffplay
            self.process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", self.file_path],
                stdout=subprocess.DEVNULL,
                stderr=stderr
            )
        self.start_time = time.monotonic()

    def get_current_time(self):
        """Returns elapsed time since start (monotonic clock v1)."""
        if self.start_time is None:
            return 0
        return time.monotonic() - self.start_time

    def stop(self):
        """Stops the audio playback."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
