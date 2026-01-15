"""
Configuration constants for Netflix AI Assistant
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MOVIES_JSON = os.path.join(DATA_DIR, "movies.json")

# Netflix Detection
NETFLIX_WINDOW_TITLE = "Netflix"
NETFLIX_WINDOW_CLASS = "ApplicationFrameWindow"

# AI Trigger
AI_PREFIX = "AI:"

# Overlay Appearance
OVERLAY_CONFIG = {
    "width": 380,
    "min_height": 100,
    "max_results": 8,
    "bg_color": "#1a1a2e",
    "fg_color": "#ffffff",
    "highlight_color": "#e50914",  # Netflix red
    "border_color": "#333355",
    "font_family": "Segoe UI",
    "font_size": 11,
    "title_font_size": 10,
    "padding": 8,
    "item_height": 52,
    "border_radius": 12,
    "shadow_offset": 4,
    "opacity": 0.97,
}

# Keyboard
KEYBINDINGS = {
    "navigate_up": "Up",
    "navigate_down": "Down",
    "select": "Return",
    "close": "Escape",
}

# Timing (milliseconds)
TIMING = {
    "overlay_delay": 50,       # Delay before showing overlay
    "position_update": 100,    # How often to update overlay position
    "input_debounce": 50,      # Debounce for input processing
    "typing_delay": 20,        # Delay between simulated keystrokes
}

# Mode
DEMO_MODE = True  # Use local JSON; set to False for API mode

# API Configuration (only used if DEMO_MODE = False)
TMDB_API_KEY = ""  # Add your TMDB API key here
OMDB_API_KEY = ""  # Add your OMDB API key here
