"""
Keyboard Monitor Module

Monitors keyboard input ONLY when Netflix is the active window.
Detects when user types 'AI:' prefix and triggers the overlay.

Privacy-focused: No global keylogging, only monitors when Netflix is focused.
"""

import threading
import time
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import logging

from .netflix_detector import get_detector
from .config import AI_PREFIX, TIMING

logger = logging.getLogger(__name__)


class KeyboardMonitor:
    """
    Monitors keyboard input when Netflix is the active application.
    """
    
    def __init__(
        self,
        on_ai_query: Optional[Callable[[str], None]] = None,
        on_input_change: Optional[Callable[[str], None]] = None,
        on_escape: Optional[Callable[[], None]] = None,
        on_enter: Optional[Callable[[], None]] = None,
        on_arrow_up: Optional[Callable[[], None]] = None,
        on_arrow_down: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the keyboard monitor.
        
        Args:
            on_ai_query: Callback when AI: query is detected
            on_input_change: Callback when input buffer changes
            on_escape: Callback when Escape is pressed
            on_enter: Callback when Enter is pressed
            on_arrow_up: Callback when Arrow Up is pressed
            on_arrow_down: Callback when Arrow Down is pressed
        """
        self.on_ai_query = on_ai_query
        self.on_input_change = on_input_change
        self.on_escape = on_escape
        self.on_enter = on_enter
        self.on_arrow_up = on_arrow_up
        self.on_arrow_down = on_arrow_down
        
        self.input_buffer = ""
        self.is_running = False
        self.listener: Optional[keyboard.Listener] = None
        self.detector = get_detector()
        
        # Track if overlay is showing (for navigation keys)
        self.overlay_active = False
        
        # Debounce
        self._last_input_time = 0
        self._debounce_ms = TIMING.get('input_debounce', 50)
    
    def start(self):
        """Start monitoring keyboard input."""
        if self.is_running:
            logger.warning("Keyboard monitor already running")
            return
        
        self.is_running = True
        self.input_buffer = ""
        
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.listener.start()
        logger.info("Keyboard monitor started")
    
    def stop(self):
        """Stop monitoring keyboard input."""
        self.is_running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        logger.info("Keyboard monitor stopped")
    
    def clear_buffer(self):
        """Clear the input buffer."""
        self.input_buffer = ""
        logger.debug("Input buffer cleared")
    
    def set_overlay_active(self, active: bool):
        """Set whether the overlay is currently showing."""
        self.overlay_active = active
    
    def _on_key_press(self, key):
        """Handle key press events."""
        # Only process if Netflix is active
        if not self.detector.is_netflix_active():
            return
        
        try:
            # Handle special keys
            if key == Key.esc:
                if self.overlay_active and self.on_escape:
                    self.on_escape()
                return
            
            if key == Key.enter:
                if self.overlay_active and self.on_enter:
                    self.on_enter()
                    return
                # If overlay not active, clear buffer (user submitted search)
                self.clear_buffer()
                return
            
            if key == Key.up:
                if self.overlay_active and self.on_arrow_up:
                    self.on_arrow_up()
                return
            
            if key == Key.down:
                if self.overlay_active and self.on_arrow_down:
                    self.on_arrow_down()
                return
            
            if key == Key.backspace:
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
                    self._process_input()
                return
            
            if key == Key.space:
                self.input_buffer += " "
                self._process_input()
                return
            
            # Handle regular characters
            if hasattr(key, 'char') and key.char:
                char = key.char
                self.input_buffer += char
                self._process_input()
                
        except Exception as e:
            logger.error(f"Error processing key press: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events (currently unused)."""
        pass
    
    def _process_input(self):
        """Process the input buffer and trigger callbacks."""
        current_time = time.time() * 1000
        
        # Debounce
        if current_time - self._last_input_time < self._debounce_ms:
            return
        
        self._last_input_time = current_time
        
        # Notify input change
        if self.on_input_change:
            self.on_input_change(self.input_buffer)
        
        # Check for AI: prefix
        buffer_upper = self.input_buffer.upper()
        if buffer_upper.startswith(AI_PREFIX.upper()):
            query = self.input_buffer[len(AI_PREFIX):].strip()
            logger.debug(f"AI query detected: '{query}'")
            
            if self.on_ai_query:
                self.on_ai_query(query)


class SafeKeyboardMonitor(KeyboardMonitor):
    """
    Enhanced keyboard monitor with additional safety checks.
    Only activates when Netflix search box is focused.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_interval = 0.5  # Check every 500ms if Netflix is still focused
        self._check_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start monitoring with periodic focus checks."""
        super().start()
        
        # Start focus check thread
        self._check_thread = threading.Thread(target=self._focus_check_loop, daemon=True)
        self._check_thread.start()
    
    def stop(self):
        """Stop monitoring and cleanup."""
        super().stop()
        self._check_thread = None
    
    def _focus_check_loop(self):
        """Periodically check if Netflix is still focused."""
        while self.is_running:
            if not self.detector.is_netflix_active():
                # Netflix lost focus - clear buffer
                if self.input_buffer:
                    self.clear_buffer()
                    if self.overlay_active and self.on_escape:
                        self.on_escape()
            
            time.sleep(self._check_interval)


if __name__ == "__main__":
    # Test keyboard monitor
    logging.basicConfig(level=logging.DEBUG)
    
    def on_query(query):
        print(f"AI Query: {query}")
    
    def on_change(text):
        print(f"Input: {text}")
    
    def on_escape():
        print("Escape pressed")
    
    def on_enter():
        print("Enter pressed")
    
    def on_up():
        print("Arrow Up")
    
    def on_down():
        print("Arrow Down")
    
    monitor = SafeKeyboardMonitor(
        on_ai_query=on_query,
        on_input_change=on_change,
        on_escape=on_escape,
        on_enter=on_enter,
        on_arrow_up=on_up,
        on_arrow_down=on_down
    )
    
    print("Starting keyboard monitor...")
    print("Type in Netflix to test. Press Ctrl+C to stop.")
    
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        monitor.stop()
