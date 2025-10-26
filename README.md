# Touch Grass Or Else

**Winner of STACS Hack the Bubble 2025 Hackathon**

This is a meticulously designed computer vision application that ensures you get enugh grass-touching every day. You get a health bar, that gradually depletes over time, as you sit in front of your computer. Once you're entirely out of health, your entire laptop stops responding to mouse and keyboard input. Your only way to get back to work is to restore your health by going outside and touching grass.The more points of contact you have -- the faster the bar fills back up (you are encouraged to lie down).

## What It Does

Touch Grass Or Else uses your webcam and computer vision to:
- **Detect grass** in your camera feed using color-based detection
- **Track your body** using MediaPipe's pose estimation to detect when your hands, feet, or other body parts inevitably make contact with grass
- **Display a health bar** that depletes over time when you're not touching grass
- **Show motivational overlays** (definitely not cursed memes) before you restore your heath bar up to at least 5%
- **Provide real-time feedback** (points of contact & contact percentage) with an unescapable fullscreen camera view showing detected grass (green overlay) and body tracking landmarks

## Installation

### Prerequisites

- Python 3.12 (or 3.8+)
- Webcam
- macOS, Linux, or Windows

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/a-nosnitram/touch-grass-or-else.git
   cd touch-grass-or-else
   ```

2. **Run the setup script:**
   ```bash
   bash touch_grass.sh
   ```

   This will:
   - Create a Python virtual environment (`.venv`)
   - Install all required dependencies
   - Launch the application

## License

This project was created for the STACS Hack the Bubble hackathon. Do with that what you will.