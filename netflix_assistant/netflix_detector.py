"""
Netflix Window Detection and UI Automation Module

Handles:
- Finding the Netflix UWP window
- Locating the search box via UI Automation
- Getting screen coordinates for overlay positioning
"""

import ctypes
from ctypes import wintypes
import win32gui
import win32process
import win32con
import win32api
from typing import Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Windows API constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# UI Automation imports
try:
    import comtypes
    import comtypes.client
    from comtypes import GUID
    HAS_UIA = True
except ImportError:
    HAS_UIA = False
    logger.warning("comtypes not available - UI Automation features disabled")

# UI Automation constants
UIA_ControlTypePropertyId = 30003
UIA_NamePropertyId = 30005
UIA_AutomationIdPropertyId = 30011
UIA_ClassNamePropertyId = 30012
UIA_EditControlTypeId = 50004
UIA_ButtonControlTypeId = 50000
TreeScope_Children = 0x2
TreeScope_Descendants = 0x4
TreeScope_Subtree = 0x7


class NetflixDetector:
    """
    Detects and interacts with the Netflix UWP application window.
    """
    
    def __init__(self):
        self.netflix_hwnd: Optional[int] = None
        self.search_box_element = None
        self.uia = None
        self._init_uia()
    
    def _init_uia(self):
        """Initialize UI Automation client."""
        if HAS_UIA:
            try:
                self.uia = comtypes.client.CreateObject(
                    "{ff48dba4-60ef-4201-aa87-54103eef594e}",  # CUIAutomation CLSID
                    interface=comtypes.gen.UIAutomationClient.IUIAutomation
                )
                logger.info("UI Automation initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize UI Automation: {e}")
                self.uia = None
    
    def find_netflix_window(self) -> Optional[int]:
        """
        Find the Netflix desktop app window.
        
        Netflix UWP runs in an ApplicationFrameWindow container.
        We look for windows with "Netflix" in the title.
        
        Returns:
            Window handle (HWND) or None if not found
        """
        netflix_windows = []
        
        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # Netflix UWP app criteria:
                    # - Title contains "Netflix"
                    # - Usually in ApplicationFrameWindow class
                    if "Netflix" in title:
                        netflix_windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'class': class_name
                        })
                        logger.debug(f"Found Netflix window: {title} ({class_name})")
                except Exception as e:
                    pass
            return True
        
        win32gui.EnumWindows(enum_callback, None)
        
        if netflix_windows:
            # Prefer ApplicationFrameWindow (UWP container)
            for win in netflix_windows:
                if win['class'] == 'ApplicationFrameWindow':
                    self.netflix_hwnd = win['hwnd']
                    logger.info(f"Selected Netflix UWP window: {win['title']}")
                    return self.netflix_hwnd
            
            # Fallback to first match
            self.netflix_hwnd = netflix_windows[0]['hwnd']
            logger.info(f"Selected Netflix window: {netflix_windows[0]['title']}")
            return self.netflix_hwnd
        
        logger.debug("Netflix window not found")
        return None
    
    def is_netflix_active(self) -> bool:
        """
        Check if Netflix is the foreground (active) window.
        
        Returns:
            True if Netflix is active, False otherwise
        """
        try:
            foreground_hwnd = win32gui.GetForegroundWindow()
            
            if foreground_hwnd == self.netflix_hwnd:
                return True
            
            # Check if foreground window title contains Netflix
            title = win32gui.GetWindowText(foreground_hwnd)
            return "Netflix" in title
        except Exception as e:
            logger.error(f"Error checking if Netflix is active: {e}")
            return False
    
    def get_netflix_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the Netflix window rectangle (position and size).
        
        Returns:
            Tuple of (left, top, right, bottom) or None
        """
        if not self.netflix_hwnd:
            self.find_netflix_window()
        
        if self.netflix_hwnd:
            try:
                rect = win32gui.GetWindowRect(self.netflix_hwnd)
                return rect
            except Exception as e:
                logger.error(f"Error getting Netflix window rect: {e}")
        
        return None
    
    def get_search_box_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the search box position using UI Automation.
        
        Returns:
            Tuple of (left, top, right, bottom) or None
        """
        if not self.uia or not self.netflix_hwnd:
            return self._get_search_box_rect_fallback()
        
        try:
            # Get root element from Netflix window
            root_element = self.uia.ElementFromHandle(self.netflix_hwnd)
            
            if not root_element:
                logger.warning("Could not get root element from Netflix window")
                return self._get_search_box_rect_fallback()
            
            # Create condition to find Edit control (search input)
            condition = self.uia.CreatePropertyCondition(
                UIA_ControlTypePropertyId,
                UIA_EditControlTypeId
            )
            
            # Search for edit control in descendants
            search_element = root_element.FindFirst(TreeScope_Descendants, condition)
            
            if search_element:
                self.search_box_element = search_element
                rect = search_element.CurrentBoundingRectangle
                logger.debug(f"Found search box at: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
                return (rect.left, rect.top, rect.right, rect.bottom)
            
            # Try finding by name containing "search"
            name_condition = self.uia.CreatePropertyCondition(
                UIA_NamePropertyId,
                "Search"
            )
            search_element = root_element.FindFirst(TreeScope_Descendants, name_condition)
            
            if search_element:
                self.search_box_element = search_element
                rect = search_element.CurrentBoundingRectangle
                logger.debug(f"Found search element by name at: ({rect.left}, {rect.top})")
                return (rect.left, rect.top, rect.right, rect.bottom)
            
            logger.warning("Search box not found via UI Automation")
            return self._get_search_box_rect_fallback()
            
        except Exception as e:
            logger.error(f"Error finding search box via UIA: {e}")
            return self._get_search_box_rect_fallback()
    
    def _get_search_box_rect_fallback(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Fallback method to estimate search box position.
        Netflix search is typically in the top-right area.
        
        Returns:
            Estimated rectangle for search box
        """
        netflix_rect = self.get_netflix_rect()
        if not netflix_rect:
            return None
        
        left, top, right, bottom = netflix_rect
        window_width = right - left
        window_height = bottom - top
        
        # Estimate: search box is typically in top area, somewhat to the left of center
        # Netflix search appears after clicking the search icon
        search_left = left + int(window_width * 0.15)
        search_top = top + 60  # Below the title bar
        search_right = left + int(window_width * 0.6)
        search_bottom = search_top + 40
        
        logger.debug(f"Using fallback search box position: ({search_left}, {search_top})")
        return (search_left, search_top, search_right, search_bottom)
    
    def is_search_box_focused(self) -> bool:
        """
        Check if the Netflix search box currently has focus.
        
        Returns:
            True if search box is focused, False otherwise
        """
        if not self.is_netflix_active():
            return False
        
        if self.uia and self.search_box_element:
            try:
                focused_element = self.uia.GetFocusedElement()
                if focused_element:
                    # Compare automation IDs or other properties
                    return True  # Simplified - assume focused if Netflix is active
            except Exception:
                pass
        
        # Fallback: If Netflix is active, assume user might be in search
        # This is less accurate but works for demo purposes
        return self.is_netflix_active()
    
    def get_dpi_scale(self) -> float:
        """
        Get the DPI scale factor for proper positioning.
        
        Returns:
            DPI scale factor (1.0 = 100%, 1.25 = 125%, etc.)
        """
        try:
            # Get DPI for the primary monitor
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except Exception:
            return 1.0


# Singleton instance for easy access
_detector = None

def get_detector() -> NetflixDetector:
    """Get or create the singleton NetflixDetector instance."""
    global _detector
    if _detector is None:
        _detector = NetflixDetector()
    return _detector


if __name__ == "__main__":
    # Test detection
    detector = NetflixDetector()
    
    print("Looking for Netflix window...")
    hwnd = detector.find_netflix_window()
    
    if hwnd:
        print(f"Found Netflix window: {hwnd}")
        print(f"Is Netflix active: {detector.is_netflix_active()}")
        
        rect = detector.get_netflix_rect()
        if rect:
            print(f"Netflix window rect: {rect}")
        
        search_rect = detector.get_search_box_rect()
        if search_rect:
            print(f"Search box rect: {search_rect}")
    else:
        print("Netflix window not found. Make sure Netflix app is open.")
