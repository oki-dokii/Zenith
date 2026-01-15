"""
Netflix AI Assistant - Main Entry Point

Orchestrates all components:
- Netflix window detection
- Keyboard monitoring
- Overlay display
- Movie search
- Netflix control
"""

import sys
import time
import logging
import argparse
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_components():
    """Import and initialize all components."""
    from .netflix_detector import get_detector
    from .keyboard_monitor import SafeKeyboardMonitor
    from .search_engine import get_search_engine
    from .overlay_window import SuggestionOverlay
    from .netflix_controller import get_controller
    
    return {
        'detector': get_detector(),
        'search_engine': get_search_engine(),
        'controller': get_controller(),
    }


class NetflixAIAssistant:
    """
    Main application class that coordinates all components.
    """
    
    def __init__(self):
        self.is_running = False
        self.overlay = None
        self.keyboard_monitor = None
        self.detector = None
        self.search_engine = None
        self.controller = None
        
        self._current_query = ""
    
    def initialize(self):
        """Initialize all components."""
        logger.info("Initializing Netflix AI Assistant...")
        
        # Import components
        from .netflix_detector import get_detector
        from .keyboard_monitor import SafeKeyboardMonitor
        from .search_engine import get_search_engine
        from .overlay_window import SuggestionOverlay
        from .netflix_controller import get_controller
        
        # Initialize detector
        self.detector = get_detector()
        
        # Initialize search engine
        self.search_engine = get_search_engine()
        logger.info(f"Loaded {len(self.search_engine.movies)} movies")
        
        # Initialize controller
        self.controller = get_controller()
        
        # Initialize overlay
        self.overlay = SuggestionOverlay(
            on_select=self._on_movie_selected,
            on_close=self._on_overlay_closed
        )
        
        # Initialize keyboard monitor
        self.keyboard_monitor = SafeKeyboardMonitor(
            on_ai_query=self._on_ai_query,
            on_input_change=self._on_input_change,
            on_escape=self._on_escape,
            on_enter=self._on_enter,
            on_arrow_up=self._on_arrow_up,
            on_arrow_down=self._on_arrow_down
        )
        
        logger.info("All components initialized")
    
    def start(self):
        """Start the assistant."""
        if self.is_running:
            logger.warning("Assistant already running")
            return
        
        logger.info("Starting Netflix AI Assistant...")
        self.is_running = True
        
        # Start overlay
        self.overlay.start()
        
        # Start keyboard monitor
        self.keyboard_monitor.start()
        
        logger.info("=" * 50)
        logger.info("Netflix AI Assistant is running!")
        logger.info("=" * 50)
        logger.info("")
        logger.info("Instructions:")
        logger.info("1. Open the Netflix desktop app")
        logger.info("2. Click on the search icon")
        logger.info("3. Type 'AI:' followed by your query")
        logger.info("   Example: 'AI: horror movies'")
        logger.info("")
        logger.info("Navigation:")
        logger.info("  Arrow Up/Down - Navigate suggestions")
        logger.info("  Enter         - Select suggestion")
        logger.info("  Escape        - Close overlay")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 50)
    
    def stop(self):
        """Stop the assistant."""
        logger.info("Stopping Netflix AI Assistant...")
        self.is_running = False
        
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()
        
        if self.overlay:
            self.overlay.stop()
        
        logger.info("Netflix AI Assistant stopped")
    
    def run(self):
        """Run the main loop."""
        try:
            while self.is_running:
                # Check if Netflix is running
                netflix_hwnd = self.detector.find_netflix_window()
                
                if netflix_hwnd:
                    # Netflix is running
                    pass
                else:
                    # Netflix not found - hide overlay if visible
                    if self.overlay and self.overlay.is_visible:
                        self.overlay.hide()
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def _on_ai_query(self, query: str):
        """Handle AI query detection."""
        logger.info(f"AI Query: '{query}'")
        self._current_query = query
        
        if not query.strip():
            # Empty query - hide overlay
            if self.overlay.is_visible:
                self.overlay.hide()
            return
        
        # Search for movies
        results = self.search_engine.search(query)
        logger.info(f"Found {len(results)} results")
        
        if results:
            # Show overlay with results
            self.overlay.show(results, query)
            self.keyboard_monitor.set_overlay_active(True)
        else:
            # No results - hide overlay
            if self.overlay.is_visible:
                self.overlay.hide()
            self.keyboard_monitor.set_overlay_active(False)
    
    def _on_input_change(self, text: str):
        """Handle input buffer changes."""
        # Only process if text still starts with AI:
        from .config import AI_PREFIX
        if not text.upper().startswith(AI_PREFIX.upper()):
            # User is typing something else - hide overlay
            if self.overlay and self.overlay.is_visible:
                self.overlay.hide()
                self.keyboard_monitor.set_overlay_active(False)
    
    def _on_escape(self):
        """Handle Escape key."""
        if self.overlay and self.overlay.is_visible:
            self.overlay.hide()
            self.keyboard_monitor.set_overlay_active(False)
            self.keyboard_monitor.clear_buffer()
    
    def _on_enter(self):
        """Handle Enter key when overlay is active."""
        if self.overlay and self.overlay.is_visible:
            self.overlay.select_current()
    
    def _on_arrow_up(self):
        """Handle Arrow Up key."""
        if self.overlay and self.overlay.is_visible:
            self.overlay.navigate_up()
    
    def _on_arrow_down(self):
        """Handle Arrow Down key."""
        if self.overlay and self.overlay.is_visible:
            self.overlay.navigate_down()
    
    def _on_movie_selected(self, movie: Dict):
        """Handle movie selection."""
        title = movie.get('title', '')
        logger.info(f"Movie selected: {title}")
        
        # Clear the keyboard buffer
        self.keyboard_monitor.clear_buffer()
        self.keyboard_monitor.set_overlay_active(False)
        
        # Search for the movie in Netflix
        if title:
            self.controller.search_for_movie(title)
    
    def _on_overlay_closed(self):
        """Handle overlay close."""
        self.keyboard_monitor.set_overlay_active(False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Netflix AI Assistant')
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug logging'
    )
    parser.add_argument(
        '--test-detection',
        action='store_true',
        help='Test Netflix window detection only'
    )
    parser.add_argument(
        '--test-overlay',
        action='store_true',
        help='Test overlay window only'
    )
    parser.add_argument(
        '--test-search',
        action='store_true',
        help='Test search engine only'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Test modes
    if args.test_detection:
        from .netflix_detector import NetflixDetector
        detector = NetflixDetector()
        hwnd = detector.find_netflix_window()
        if hwnd:
            print(f"✓ Netflix window found: {hwnd}")
            print(f"  Active: {detector.is_netflix_active()}")
            print(f"  Rect: {detector.get_netflix_rect()}")
            print(f"  Search box: {detector.get_search_box_rect()}")
        else:
            print("✗ Netflix window not found")
        return
    
    if args.test_overlay:
        from .overlay_window import SuggestionOverlay
        
        overlay = SuggestionOverlay()
        overlay.start()
        time.sleep(1)
        
        test_movies = [
            {"title": "The Conjuring", "year": 2013, "rating": 7.5, "genres": ["horror"]},
            {"title": "Hereditary", "year": 2018, "rating": 7.3, "genres": ["horror"]},
            {"title": "Get Out", "year": 2017, "rating": 7.7, "genres": ["horror"]},
        ]
        
        overlay.show(test_movies, "horror")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            overlay.stop()
        return
    
    if args.test_search:
        from .search_engine import MovieSearchEngine
        
        engine = MovieSearchEngine()
        print(f"Loaded {len(engine.movies)} movies")
        
        test_queries = ["horror movies", "comedy", "sci-fi space", "romance"]
        for query in test_queries:
            print(f"\n🔍 '{query}':")
            for movie in engine.search(query)[:5]:
                print(f"   • {movie['title']} ({movie['year']}) ★{movie['rating']}")
        return
    
    # Run main application
    assistant = NetflixAIAssistant()
    assistant.initialize()
    assistant.start()
    assistant.run()


if __name__ == "__main__":
    main()
