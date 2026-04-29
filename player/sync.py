import time

class SyncManager:
    def __init__(self, audio, video, renderer):
        self.audio = audio
        self.video = video
        self.renderer = renderer
        self.frame_duration = 1.0 / video.fps

    def play(self):
        self.video.start()

        # Read the first frame BEFORE starting audio to ensure sync
        frame_data = self.video.next_frame()
        if frame_data is None:
            self.video.stop()
            return

        if self.audio:
            self.audio.start()
            clock_start = None
        else:
            clock_start = time.monotonic()
        self.renderer.render(frame_data)

        frame_count = 1
        try:
            while True:
                frame_data = self.video.next_frame()
                if frame_data is None:
                    break

                video_time = frame_count * self.frame_duration
                if self.audio:
                    audio_time = self.audio.get_current_time()
                else:
                    audio_time = time.monotonic() - clock_start

                # Sync logic: Only skip if we are significantly behind
                if video_time < audio_time - (self.frame_duration * 4):
                    frame_count += 1
                    continue

                # Wait if we are ahead
                if video_time > audio_time:
                    wait_time = video_time - audio_time
                    if wait_time > 0.001:
                        time.sleep(wait_time)

                self.renderer.render(frame_data)
                frame_count += 1
        finally:
            self.stop()

    def stop(self):
        """Stops both audio and video subprocesses."""
        if self.audio:
            self.audio.stop()
        self.video.stop()
