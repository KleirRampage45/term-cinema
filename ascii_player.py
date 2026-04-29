#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import shutil
import signal
import sys

# Ensure the 'player' package can be found regardless of how the script is invoked.
# Local checkout imports take precedence so development runs do not accidentally
# load an older globally installed package.
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
global_dir = "/usr/share/ascii-player"

if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if os.path.exists(global_dir) and global_dir not in sys.path:
    sys.path.append(global_dir)

from player.audio import AudioController
from player.video import VideoDecoder
from player.renderer import Renderer
from player.sync import SyncManager

DEMO_PATHS = (
    Path("/usr/share/ascii-player/badapple.mp4"),
    Path(__file__).resolve().with_name("badapple.mp4"),
)


def setup_terminal():
    # Hide cursor, switch to alternate buffer
    sys.stdout.write("\033[?25l\033[?1049h")
    sys.stdout.flush()

def cleanup_terminal():
    # Reset colors, clear screen, show cursor, exit alternate buffer
    # We use a comprehensive sequence to ensure the terminal is usable
    sys.stdout.write("\033[0m\033[2J\033[H\033[?25h\033[?1049l")
    sys.stdout.flush()

def signal_handler(sig, frame):
    # This will trigger the finally block in main
    sys.exit(0)


def parse_size(value):
    try:
        cols, rows = value.lower().split("x", 1)
        cols = int(cols)
        rows = int(rows)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("size must be formatted as COLSxROWS, for example 120x36") from exc

    if cols <= 0 or rows <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return cols, rows


def find_demo_video():
    for path in DEMO_PATHS:
        if path.exists():
            return path
    return None


def check_dependencies(use_audio):
    required = ["ffmpeg", "chafa"]
    missing = [tool for tool in required if shutil.which(tool) is None]

    if use_audio and shutil.which("mpv") is None and shutil.which("ffplay") is None:
        missing.append("mpv or ffplay")

    if missing:
        raise RuntimeError("Missing required command: " + ", ".join(missing))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Play videos as high-color terminal art. Built for Bad Apple, useful for anything."
    )
    parser.add_argument("file", nargs="?", help="Path to the video file")
    parser.add_argument("--demo", action="store_true", help="Play the bundled Bad Apple demo if it is installed")
    parser.add_argument("--fps", type=int, default=24, help="Playback FPS (default: 24)")
    parser.add_argument("--size", type=parse_size, help="Terminal render size as COLSxROWS; defaults to current terminal")
    parser.add_argument("--frame-width", type=int, default=240, help="Intermediate decoded frame width (default: 240)")
    parser.add_argument(
        "--symbols",
        default="block",
        choices=("block", "half", "braille", "ascii", "space"),
        help="Chafa symbol set (default: block)",
    )
    parser.add_argument(
        "--colors",
        default="full",
        choices=("full", "256", "240", "16", "16/8", "8", "2", "none"),
        help="Chafa color mode (default: full)",
    )
    parser.add_argument("--no-audio", action="store_true", help="Disable audio playback")
    parser.add_argument("--loop", action="store_true", help="Loop playback until interrupted")
    parser.add_argument("--debug", action="store_true", help="Show subprocess errors and tracebacks")
    return parser


def resolve_video_path(args):
    if args.demo:
        demo = find_demo_video()
        if demo is None:
            raise FileNotFoundError("Bad Apple demo video was not found. Pass a video path instead.")
        return demo

    if not args.file:
        raise ValueError("No video file provided. Pass a path or use --demo.")

    path = Path(args.file).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File '{args.file}' not found.")
    return path


def run_once(video_path, args):
    audio = None if args.no_audio else AudioController(str(video_path), debug=args.debug)
    video = VideoDecoder(str(video_path), fps=args.fps, frame_width=args.frame_width, debug=args.debug)
    renderer = Renderer(size=args.size, symbols=args.symbols, colors=args.colors, debug=args.debug)
    sync = SyncManager(audio, video, renderer)
    sync.play()


def default_argv(argv):
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    invoked_as_badapple = Path(sys.argv[0]).name == "badapple"

    if invoked_as_badapple and "--demo" not in effective_argv:
        first_arg_is_file = bool(effective_argv) and not effective_argv[0].startswith("-")
        if not first_arg_is_file:
            effective_argv.insert(0, "--demo")

    return effective_argv


def main(argv=None):
    # Handle both Ctrl+C and termination signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = build_parser()
    args = parser.parse_args(default_argv(argv))
    terminal_ready = False

    if args.fps <= 0:
        parser.error("--fps must be greater than zero")
    if args.frame_width <= 0:
        parser.error("--frame-width must be greater than zero")

    error = None
    try:
        video_path = resolve_video_path(args)
        check_dependencies(use_audio=not args.no_audio)
        setup_terminal()
        terminal_ready = True
        while True:
            run_once(video_path, args)
            if not args.loop:
                break
    except BaseException as e:
        # Catching BaseException to include KeyboardInterrupt and SystemExit
        if not isinstance(e, (KeyboardInterrupt, SystemExit)):
            error = e
    finally:
        if terminal_ready:
            cleanup_terminal()
        if error:
            print(f"Error: {error}", file=sys.stderr)
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
