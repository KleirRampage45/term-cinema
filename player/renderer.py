import subprocess
import shutil
import sys

class Renderer:
    def __init__(self, size=None, symbols="block", colors="full", debug=False):
        self.size = size
        self.symbols = symbols
        self.colors = colors
        self.debug = debug

    def render(self, ppm_data):
        """Pipes image data to chafa and prints it directly to terminal stdout."""
        if self.size:
            cols, lines = self.size
        else:
            size = shutil.get_terminal_size((80, 24))
            cols = size.columns
            lines = max(1, size.lines - 1)
        size_str = f"{cols}x{lines}"

        try:
            # Position cursor at top-left
            sys.stdout.buffer.write(b"\033[H")
            sys.stdout.buffer.flush()

            # Start chafa with full color support
            process = subprocess.Popen(
                ["chafa", "--symbols", self.symbols, "--colors", self.colors, "--size", size_str, "-"],
                stdin=subprocess.PIPE,
                stdout=sys.stdout.buffer,
                stderr=None if self.debug else subprocess.DEVNULL
            )
            process.communicate(input=ppm_data, timeout=2.0)
            sys.stdout.buffer.flush()
        except Exception as exc:
            if self.debug:
                raise RuntimeError("Failed to render frame with chafa") from exc
