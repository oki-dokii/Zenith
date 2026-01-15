# Netflix AI Assistant

A lightweight Windows desktop assistant that integrates with the Netflix UWP app. When you type `AI:` in the Netflix search box, a smart overlay appears with AI-curated movie suggestions.

![Demo](docs/demo.gif)

## Features

- 🎬 **Inline Overlay**: Appears directly below the Netflix search box
- ⌨️ **Keyboard Navigation**: Use Arrow Up/Down, Enter, Escape
- 🖱️ **Mouse Support**: Click to select suggestions
- 🔍 **Smart Search**: Fuzzy matching for genres and titles
- 🔒 **Privacy-First**: Only monitors input when Netflix is active
- 🎨 **Netflix-Themed UI**: Dark mode with Netflix red accents

## Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8+
- Netflix Desktop App (from Microsoft Store)

### Installation

```bash
# Navigate to the project
cd netflix_assistant

# Install dependencies
pip install -r requirements.txt

# Run the assistant
python -m netflix_assistant.main
```

### Usage

1. **Open Netflix** desktop app (not browser)
2. **Click the search icon** in Netflix
3. **Type `AI:`** followed by your query:
   ```
   AI: horror movies
   AI: funny comedy
   AI: sci-fi space
   AI: romantic movies
   ```
4. **Navigate suggestions**:
   - `↑` `↓` Arrow keys to move selection
   - `Enter` to select
   - `Escape` to close
5. **Selected title** is automatically searched in Netflix

## How It Works

### Netflix Detection

The assistant uses Windows APIs to detect the Netflix window:

```python
# Netflix UWP runs in ApplicationFrameWindow container
# Detected by window title containing "Netflix"
win32gui.EnumWindows(callback, None)
```

### Search Box Identification

Uses Windows UI Automation to find the search input:

```python
# Navigate UIA tree to find Edit control
uia = comtypes.client.CreateObject("CUIAutomation")
root = uia.ElementFromHandle(netflix_hwnd)
search_box = root.FindFirst(TreeScope_Descendants, edit_condition)
```

### Overlay Positioning

The overlay is positioned relative to the search box using screen coordinates:

```python
# Get search box bounding rectangle
rect = search_box.CurrentBoundingRectangle
# Position overlay just below
overlay_y = rect.bottom + 5
```

## Project Structure

```
netflix_assistant/
├── __init__.py           # Package init
├── main.py               # Entry point & orchestration
├── config.py             # Configuration constants
├── netflix_detector.py   # Window & element detection
├── keyboard_monitor.py   # Safe keyboard capture
├── overlay_window.py     # Transparent overlay UI
├── search_engine.py      # Movie search & matching
├── netflix_controller.py # Text injection & search trigger
├── requirements.txt      # Dependencies
└── data/
    └── movies.json       # Demo movie dataset
```

## Configuration

Edit `config.py` to customize:

```python
# Overlay appearance
OVERLAY_CONFIG = {
    "width": 380,
    "bg_color": "#1a1a2e",
    "highlight_color": "#e50914",  # Netflix red
    "opacity": 0.97,
}

# Keybindings
KEYBINDINGS = {
    "navigate_up": "Up",
    "navigate_down": "Down",
    "select": "Return",
    "close": "Escape",
}
```

## Test Modes

```bash
# Test Netflix detection
python -m netflix_assistant.main --test-detection

# Test overlay window
python -m netflix_assistant.main --test-overlay

# Test search engine
python -m netflix_assistant.main --test-search

# Enable debug logging
python -m netflix_assistant.main --debug
```

## Supported Search Queries

| Query Type | Examples |
|------------|----------|
| Genre | `horror`, `comedy`, `action`, `drama`, `sci-fi` |
| Mood | `scary`, `funny`, `romantic`, `exciting` |
| Combined | `horror movies`, `funny comedy`, `space sci-fi` |
| Specific | `The Conjuring`, `Inception` |

## Privacy & Safety

- ✅ **No global keylogging** - Only monitors when Netflix is active
- ✅ **No data collection** - All processing is local
- ✅ **No external APIs** - Demo mode uses local JSON
- ✅ **Transparent operation** - Open source, auditable code

## Troubleshooting

### Netflix not detected

1. Make sure Netflix is the **desktop app**, not browser
2. Ensure Netflix window is visible (not minimized)
3. Try running with `--debug` flag for more info

### Overlay not appearing

1. Type `AI:` (with colon) followed by space
2. Make sure Netflix search box is focused
3. Check if overlay is appearing off-screen

### Search not triggering

1. Netflix must be in foreground when selecting
2. Try clicking into Netflix search first
3. Some Netflix versions may have different search behavior

## Technical Details

### System Requirements

- **OS**: Windows 10/11 (UWP support required)
- **Python**: 3.8+ with tkinter
- **RAM**: <50MB typical usage
- **CPU**: Minimal (event-driven architecture)

### Dependencies

| Package | Purpose |
|---------|---------|
| `pywin32` | Windows API access |
| `comtypes` | UI Automation COM interface |
| `pynput` | Keyboard monitoring |
| `tkinter` | Overlay window (built-in) |

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Netflix for the inspiration
- Windows UI Automation documentation
- Python community for excellent Windows libraries
