import subprocess
import struct

class VideoDecoder:
    def __init__(self, file_path, fps=24, frame_width=240, debug=False):
        self.file_path = file_path
        self.fps = fps
        self.frame_width = frame_width
        self.debug = debug
        self.process = None

    def start(self):
        """Starts ffmpeg to pipe PNG frames (scaled for terminal)."""
        command = [
            "ffmpeg",
            "-i", self.file_path,
            "-vf", f"fps={self.fps},scale={self.frame_width}:-1",
            "-f", "image2pipe",
            "-vcodec", "png",
            "-loglevel", "error" if self.debug else "quiet",
            "-"
        ]
        stderr = None if self.debug else subprocess.DEVNULL
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr, bufsize=10**7)

    def next_frame(self):
        """Reads the next PNG frame from the pipe."""
        if self.process is None or self.process.stdout is None:
            return None

        try:
            # PNG signature
            sig = self.process.stdout.read(8)
            if not sig or sig != b"\x89PNG\r\n\x1a\n":
                return None

            chunks = [sig]
            while True:
                # Read chunk length (4 bytes) and type (4 bytes)
                header = self.process.stdout.read(8)
                if not header: break
                chunks.append(header)

                length = struct.unpack(">I", header[:4])[0]
                chunk_type = header[4:]

                # Read data + CRC (length + 4 bytes)
                data_and_crc = self.process.stdout.read(length + 4)
                chunks.append(data_and_crc)

                if chunk_type == b"IEND":
                    break

            return b"".join(chunks)
        except Exception as exc:
            if self.debug:
                raise RuntimeError("Failed to read decoded video frame") from exc
            return None

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
