# Term Cinema

A Konsole-friendly terminal video player built around the classic Bad Apple test case. It uses `ffmpeg` for frame decoding, `chafa` for high-color terminal rendering, and `mpv` or `ffplay` for audio.

It is meant to make Bad Apple look good in a terminal, but it can play regular video files too.

## Requirements

- `ffmpeg`
- `chafa`
- `mpv` or `ffplay` for audio
- A Truecolor terminal such as Konsole, Alacritty, or Kitty
- A monospace font

## Installation

### From this checkout

```bash
python -m pip install .
```

### Arch Linux

```bash
git clone https://github.com/asukate/ascii-player
cd ascii-player
makepkg -si
```

## Usage

```bash
ascii-player path/to/video.mp4 --fps 24
```

Play the bundled Bad Apple demo when installed by the package:

```bash
badapple
```

or:

```bash
ascii-player --demo
```

Useful Konsole-oriented examples:

```bash
ascii-player badapple.mp4 --size 120x36 --symbols block --colors full
ascii-player video.mp4 --fps 30 --frame-width 320
ascii-player video.mp4 --no-audio --loop --symbols ascii --colors none
```

## Options

- `--fps`: Playback FPS, default `24`.
- `--size`: Render size in terminal cells, for example `120x36`.
- `--frame-width`: Intermediate decoded frame width before Chafa renders it.
- `--symbols`: Chafa symbol class, including `block`, `half`, `braille`, `ascii`, and `space`.
- `--colors`: Chafa color mode, including `full`, `256`, `16`, and `none`.
- `--no-audio`: Disable audio playback.
- `--loop`: Repeat playback until interrupted.
- `--debug`: Show subprocess errors and tracebacks.

## Notes

Bad Apple is a useful stress test because the sharp black-and-white animation exposes sync, scaling, and frame-drop problems quickly. For best results in Konsole, use a Truecolor profile and a font with consistent block glyphs.
