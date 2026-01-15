"""
Netflix Controller Module

Handles injecting text into Netflix search box and triggering search.
Uses UI Automation patterns with fallback to simulated keyboard input.
"""

import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import logging
from typing import Optional

from pynput.keyboard import Controller, Key

from .netflix_detector import get_detector
from .config import TIMING

logger = logging.getLogger(__name__)

# Virtual key codes
VK_RETURN = 0x0D
VK_BACK = 0x08
VK_DELETE = 0x2E
VK_HOME = 0x24
VK_END = 0x23
VK_CONTROL = 0x11
VK_A = 0x41

# Windows input types
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [('ki', KEYBDINPUT)]
    
    _anonymous_ = ['_input']
    _fields_ = [
        ('type', wintypes.DWORD),
        ('_input', _INPUT_UNION)
    ]


class NetflixController:
    """
    Controls the Netflix search box by injecting text and triggering search.
    """
    
    def __init__(self):
        self.detector = get_detector()
        self.keyboard = Controller()
        self.typing_delay = TIMING.get('typing_delay', 20) / 1000.0
    
    def clear_search_box(self) -> bool:
        """
        Clear the current content of the Netflix search box.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try UI Automation first
            if self._clear_via_uia():
                return True
            
            # Fallback to keyboard simulation
            return self._clear_via_keyboard()
            
        except Exception as e:
            logger.error(f"Error clearing search box: {e}")
            return False
    
    def _clear_via_uia(self) -> bool:
        """Clear search box using UI Automation ValuePattern."""
        try:
            if not self.detector.search_box_element:
                self.detector.get_search_box_rect()
            
            if self.detector.search_box_element:
                # Try to get ValuePattern
                # For now, fallback to keyboard (UWP apps often don't support ValuePattern)
                return False
                
        except Exception as e:
            logger.debug(f"UIA clear failed: {e}")
            return False
    
    def _clear_via_keyboard(self) -> bool:
        """Clear search box using keyboard simulation (Ctrl+A, Delete)."""
        try:
            # Ensure Netflix is active
            if not self.detector.is_netflix_active():
                logger.warning("Netflix is not active, cannot clear search box")
                return False
            
            # Select all (Ctrl+A)
            self.keyboard.press(Key.ctrl)
            self.keyboard.press('a')
            self.keyboard.release('a')
            self.keyboard.release(Key.ctrl)
            
            time.sleep(0.05)
            
            # Delete selected text
            self.keyboard.press(Key.delete)
            self.keyboard.release(Key.delete)
            
            time.sleep(0.05)
            
            logger.debug("Search box cleared via keyboard")
            return True
            
        except Exception as e:
            logger.error(f"Keyboard clear failed: {e}")
            return False
    
    def set_search_text(self, text: str) -> bool:
        """
        Set the Netflix search box text.
        
        Args:
            text: The text to set (movie title)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try UI Automation first
            if self._set_text_via_uia(text):
                return True
            
            # Fallback to keyboard simulation
            return self._set_text_via_keyboard(text)
            
        except Exception as e:
            logger.error(f"Error setting search text: {e}")
            return False
    
    def _set_text_via_uia(self, text: str) -> bool:
        """Set text using UI Automation ValuePattern."""
        try:
            if not self.detector.search_box_element:
                self.detector.get_search_box_rect()
            
            if self.detector.search_box_element:
                # Try to get and use ValuePattern
                # Most UWP apps require keyboard fallback
                return False
                
        except Exception as e:
            logger.debug(f"UIA set text failed: {e}")
            return False
    
    def _set_text_via_keyboard(self, text: str) -> bool:
        """Set text using keyboard simulation (type each character)."""
        try:
            # Ensure Netflix is active
            if not self.detector.is_netflix_active():
                logger.warning("Netflix is not active, cannot set search text")
                return False
            
            # Type each character
            for char in text:
                self.keyboard.press(char)
                self.keyboard.release(char)
                time.sleep(self.typing_delay)
            
            logger.debug(f"Typed search text: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Keyboard type failed: {e}")
            return False
    
    def trigger_search(self) -> bool:
        """
        Trigger Netflix search (press Enter).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure Netflix is active
            if not self.detector.is_netflix_active():
                logger.warning("Netflix is not active, cannot trigger search")
                return False
            
            # Small delay before Enter
            time.sleep(0.1)
            
            # Press Enter
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            
            logger.info("Search triggered")
            return True
            
        except Exception as e:
            logger.error(f"Error triggering search: {e}")
            return False
    
    def search_for_movie(self, title: str) -> bool:
        """
        Complete flow: focus Netflix, clear search, type title, trigger search.
        
        Args:
            title: Movie title or genre to search for
        
        Returns:
            True if all steps succeeded, False otherwise
        """
        logger.info(f"Searching for: {title}")
        
        # Step 0: Focus Netflix window first
        if not self.focus_netflix_search():
            logger.warning("Could not focus Netflix, attempting anyway")
        
        time.sleep(0.3)
        
        # Step 1: Clear existing search
        if not self.clear_search_box():
            logger.warning("Failed to clear search box, continuing anyway")
        
        time.sleep(0.15)
        
        # Step 2: Type the search text
        if not self.set_search_text(title):
            logger.error("Failed to set search text")
            return False
        
        time.sleep(0.3)
        
        # Step 3: Trigger search
        if not self.trigger_search():
            logger.error("Failed to trigger search")
            return False
        
        logger.info(f"Search completed for: {title}")
        return True
    
    def focus_netflix_search(self) -> bool:
        """
        Attempt to focus the Netflix search box.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find Netflix window
            hwnd = self.detector.find_netflix_window()
            if not hwnd:
                logger.warning("Netflix window not found")
                return False
            
            # Bring Netflix to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            
            # Try to click on search area or use keyboard shortcut
            # Netflix desktop app: Ctrl+S or clicking search icon
            # For demo, we assume user has already clicked on search
            
            return True
            
        except Exception as e:
            logger.error(f"Error focusing Netflix search: {e}")
            return False


# Singleton instance
_controller = None

def get_controller() -> NetflixController:
    """Get or create the singleton controller instance."""
    global _controller
    if _controller is None:
        _controller = NetflixController()
    return _controller


if __name__ == "__main__":
    # Test controller
    logging.basicConfig(level=logging.DEBUG)
    
    print("Netflix Controller Test")
    print("=" * 40)
    print("This will attempt to control the Netflix search box.")
    print("Make sure Netflix app is open and search is focused.")
    print()
    
    input("Press Enter when ready...")
    
    controller = NetflixController()
    
    # Test search
    title = "The Conjuring"
    print(f"Searching for: {title}")
    
    success = controller.search_for_movie(title)
    
    if success:
        print("✓ Search completed successfully!")
    else:
        print("✗ Search failed")
