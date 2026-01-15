"""
Overlay Window Module

Creates a transparent, always-on-top overlay that displays movie suggestions.
Positioned near the Netflix search box with keyboard and mouse navigation.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import List, Dict, Callable, Optional
import threading
import logging

from .config import OVERLAY_CONFIG, TIMING
from .netflix_detector import get_detector

logger = logging.getLogger(__name__)


class SuggestionOverlay:
    """
    A transparent overlay window that displays movie suggestions.
    """
    
    def __init__(
        self,
        on_select: Optional[Callable[[Dict], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        on_genre_select: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the overlay.
        
        Args:
            on_select: Callback when a movie is selected
            on_close: Callback when overlay is closed
            on_genre_select: Callback when a genre is selected
        """
        self.on_select = on_select
        self.on_close = on_close
        self.on_genre_select = on_genre_select
        
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[tk.Frame] = None
        self.items: List[Dict] = []
        self.genres: List[Dict] = []
        self.item_frames: List[tk.Frame] = []
        self.selected_index = 0
        self.is_visible = False
        self.query = ""
        
        self.detector = get_detector()
        self._position_update_id = None
        
        # Config shortcuts
        self.cfg = OVERLAY_CONFIG
        
        # Initialize in a separate thread
        self._init_thread: Optional[threading.Thread] = None
        self._tk_ready = threading.Event()
    
    def _create_window(self):
        """Create the tkinter window and widgets."""
        self.root = tk.Tk()
        self.root.title("Netflix AI Assistant")
        
        # Window configuration for overlay behavior
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', self.cfg['opacity'])  # Transparency
        
        # Make window click-through when not interacting
        # self.root.attributes('-transparentcolor', self.cfg['bg_color'])
        
        # Set initial size
        width = self.cfg['width']
        height = self.cfg['min_height']
        self.root.geometry(f"{width}x{height}+100+100")
        
        # Configure colors
        self.root.configure(bg=self.cfg['bg_color'])
        
        # Create main container with rounded appearance
        self.main_frame = tk.Frame(
            self.root,
            bg=self.cfg['bg_color'],
            highlightbackground=self.cfg['border_color'],
            highlightthickness=2
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header
        self.header_frame = tk.Frame(self.main_frame, bg=self.cfg['bg_color'])
        self.header_frame.pack(fill=tk.X, padx=self.cfg['padding'], pady=(self.cfg['padding'], 4))
        
        self.header_label = tk.Label(
            self.header_frame,
            text="🎬 AI Suggestions",
            font=(self.cfg['font_family'], self.cfg['title_font_size'], 'bold'),
            fg=self.cfg['highlight_color'],
            bg=self.cfg['bg_color'],
            anchor='w'
        )
        self.header_label.pack(side=tk.LEFT)
        
        self.query_label = tk.Label(
            self.header_frame,
            text="",
            font=(self.cfg['font_family'], self.cfg['title_font_size'] - 1),
            fg='#888888',
            bg=self.cfg['bg_color'],
            anchor='e'
        )
        self.query_label.pack(side=tk.RIGHT)
        
        # Separator
        sep = tk.Frame(self.main_frame, bg=self.cfg['border_color'], height=1)
        sep.pack(fill=tk.X, padx=self.cfg['padding'])
        
        # Genre pills container
        self.genre_frame = tk.Frame(self.main_frame, bg=self.cfg['bg_color'])
        self.genre_frame.pack(fill=tk.X, padx=self.cfg['padding'], pady=(self.cfg['padding'], 0))
        
        # Items container
        self.items_frame = tk.Frame(self.main_frame, bg=self.cfg['bg_color'])
        self.items_frame.pack(fill=tk.BOTH, expand=True, padx=self.cfg['padding'], pady=self.cfg['padding'])
        
        # Bind keyboard events
        self.root.bind('<Up>', self._on_key_up)
        self.root.bind('<Down>', self._on_key_down)
        self.root.bind('<Return>', self._on_key_enter)
        self.root.bind('<Escape>', self._on_key_escape)
        
        # Start hidden
        self.root.withdraw()
        
        logger.info("Overlay window created")
    
    def start(self):
        """Start the overlay window in a separate thread."""
        self._init_thread = threading.Thread(target=self._run_mainloop, daemon=True)
        self._init_thread.start()
        
        # Wait for tkinter to be ready
        self._tk_ready.wait(timeout=5)
        logger.info("Overlay started")
    
    def _run_mainloop(self):
        """Run the tkinter mainloop in a separate thread."""
        self._create_window()
        self._tk_ready.set()
        self.root.mainloop()
    
    def stop(self):
        """Stop and destroy the overlay window."""
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error stopping overlay: {e}")
        
        self.root = None
        logger.info("Overlay stopped")
    
    def show(self, items: List[Dict], query: str = "", genres: List[Dict] = None):
        """
        Show the overlay with the given items.
        
        Args:
            items: List of movie dictionaries to display
            query: The current search query
            genres: List of matching genre dictionaries to display
        """
        if not self.root:
            logger.warning("Overlay not initialized")
            return
        
        self.items = items
        self.genres = genres or []
        self.query = query
        self.selected_index = 0
        
        # Update on main thread
        self.root.after(0, lambda: self._update_display())
    
    def hide(self):
        """Hide the overlay."""
        if not self.root:
            return
        
        self.is_visible = False
        self.root.after(0, lambda: self.root.withdraw())
        
        if self.on_close:
            self.on_close()
    
    def _update_display(self):
        """Update the overlay display with current items."""
        if not self.root or not self.main_frame:
            return
        
        # Update query label
        if self.query:
            self.query_label.configure(text=f'"{self.query}"')
        else:
            self.query_label.configure(text='')
        
        # Clear existing genre pills
        for widget in self.genre_frame.winfo_children():
            widget.destroy()
        
        # Display genre pills if available
        if self.genres:
            genre_label = tk.Label(
                self.genre_frame,
                text="Genres:",
                font=(self.cfg['font_family'], self.cfg['font_size'] - 1),
                fg='#888888',
                bg=self.cfg['bg_color']
            )
            genre_label.pack(side=tk.LEFT, padx=(0, 8))
            
            for genre in self.genres:
                pill = self._create_genre_pill(genre)
                pill.pack(side=tk.LEFT, padx=2)
        
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.item_frames.clear()
        
        if not self.items:
            # Show "no results" message
            no_results = tk.Label(
                self.items_frame,
                text="No matching movies found",
                font=(self.cfg['font_family'], self.cfg['font_size']),
                fg='#666666',
                bg=self.cfg['bg_color']
            )
            no_results.pack(pady=20)
        else:
            # Create item frames
            for i, movie in enumerate(self.items):
                frame = self._create_item_frame(i, movie)
                self.item_frames.append(frame)
        
        # Update window size
        item_count = max(1, len(self.items))
        height = 60 + (item_count * self.cfg['item_height'])
        height = min(height, 500)  # Max height
        
        self.root.geometry(f"{self.cfg['width']}x{height}")
        
        # Position overlay
        self._update_position()
        
        # Show window
        self.root.deiconify()
        self.root.lift()
        self.is_visible = True
        
        # Highlight selected item
        self._update_selection()
    
    def _create_genre_pill(self, genre: Dict) -> tk.Frame:
        """Create a clickable genre pill button."""
        pill = tk.Frame(
            self.genre_frame,
            bg='#3a3a3a',
            cursor='hand2',
            padx=8,
            pady=4
        )
        
        # Genre icon and name
        icon = genre.get('icon', '🎬')
        name = genre.get('name', 'Genre')
        search_term = genre.get('search_term', name.lower())
        
        label = tk.Label(
            pill,
            text=f"{icon} {name}",
            font=(self.cfg['font_family'], self.cfg['font_size'] - 1, 'bold'),
            fg='#e50914',
            bg='#3a3a3a',
            cursor='hand2'
        )
        label.pack()
        
        # Bind click event
        def on_genre_click(event):
            if self.on_genre_select:
                self.on_genre_select(search_term)
                self.hide()
        
        pill.bind('<Button-1>', on_genre_click)
        label.bind('<Button-1>', on_genre_click)
        
        # Hover effect
        def on_enter(event):
            pill.configure(bg='#4a4a4a')
            label.configure(bg='#4a4a4a')
        
        def on_leave(event):
            pill.configure(bg='#3a3a3a')
            label.configure(bg='#3a3a3a')
        
        pill.bind('<Enter>', on_enter)
        pill.bind('<Leave>', on_leave)
        label.bind('<Enter>', on_enter)
        label.bind('<Leave>', on_leave)
        
        return pill
    
    def _create_item_frame(self, index: int, movie: Dict) -> tk.Frame:
        """Create a frame for a single movie item."""
        frame = tk.Frame(
            self.items_frame,
            bg=self.cfg['bg_color'],
            cursor='hand2'
        )
        frame.pack(fill=tk.X, pady=2)
        
        # Movie info container
        info_frame = tk.Frame(frame, bg=self.cfg['bg_color'])
        info_frame.pack(fill=tk.X, padx=8, pady=6)
        
        # Title and year
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        rating = movie.get('rating', 'N/A')
        
        title_text = f"{title}"
        if year:
            title_text += f" ({year})"
        
        title_label = tk.Label(
            info_frame,
            text=title_text,
            font=(self.cfg['font_family'], self.cfg['font_size'], 'bold'),
            fg=self.cfg['fg_color'],
            bg=self.cfg['bg_color'],
            anchor='w'
        )
        title_label.pack(anchor='w')
        
        # Rating and genres
        genres = movie.get('genres', [])[:3]
        genre_text = ' • '.join(g.capitalize() for g in genres)
        meta_text = f"★ {rating}"
        if genre_text:
            meta_text += f"  |  {genre_text}"
        
        meta_label = tk.Label(
            info_frame,
            text=meta_text,
            font=(self.cfg['font_family'], self.cfg['font_size'] - 1),
            fg='#999999',
            bg=self.cfg['bg_color'],
            anchor='w'
        )
        meta_label.pack(anchor='w')
        
        # Bind click events
        for widget in [frame, info_frame, title_label, meta_label]:
            widget.bind('<Button-1>', lambda e, idx=index: self._on_click(idx))
            widget.bind('<Enter>', lambda e, idx=index: self._on_hover(idx))
        
        # Store reference to movie
        frame.movie = movie
        
        return frame
    
    def _update_selection(self):
        """Update the visual selection highlight."""
        for i, frame in enumerate(self.item_frames):
            if i == self.selected_index:
                # Highlight selected
                self._set_frame_bg(frame, self.cfg['highlight_color'])
            else:
                # Normal background
                self._set_frame_bg(frame, self.cfg['bg_color'])
    
    def _set_frame_bg(self, frame: tk.Frame, color: str):
        """Recursively set background color for frame and children."""
        frame.configure(bg=color)
        for child in frame.winfo_children():
            try:
                child.configure(bg=color)
                if hasattr(child, 'winfo_children'):
                    self._set_frame_bg(child, color)
            except Exception:
                pass
    
    def _update_position(self):
        """Update overlay position relative to Netflix search box."""
        search_rect = self.detector.get_search_box_rect()
        
        if search_rect:
            left, top, right, bottom = search_rect
            
            # Position overlay below the search box
            x = left
            y = bottom + 5
            
            # Get screen dimensions to avoid going off-screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Adjust if overlay would go off-screen
            overlay_width = self.cfg['width']
            if x + overlay_width > screen_width:
                x = screen_width - overlay_width - 10
            
            self.root.geometry(f"+{x}+{y}")
            logger.debug(f"Overlay positioned at ({x}, {y})")
        else:
            # Fallback: center on screen
            logger.warning("Could not get search box rect, using fallback position")
    
    def navigate_up(self):
        """Navigate selection up."""
        if self.items and self.selected_index > 0:
            self.selected_index -= 1
            self.root.after(0, self._update_selection)
    
    def navigate_down(self):
        """Navigate selection down."""
        if self.items and self.selected_index < len(self.items) - 1:
            self.selected_index += 1
            self.root.after(0, self._update_selection)
    
    def select_current(self):
        """Select the currently highlighted item."""
        if self.items and 0 <= self.selected_index < len(self.items):
            movie = self.items[self.selected_index]
            logger.info(f"Selected: {movie.get('title')}")
            
            if self.on_select:
                self.on_select(movie)
            
            self.hide()
    
    def _on_key_up(self, event):
        """Handle Up arrow key."""
        self.navigate_up()
        return 'break'
    
    def _on_key_down(self, event):
        """Handle Down arrow key."""
        self.navigate_down()
        return 'break'
    
    def _on_key_enter(self, event):
        """Handle Enter key."""
        self.select_current()
        return 'break'
    
    def _on_key_escape(self, event):
        """Handle Escape key."""
        self.hide()
        return 'break'
    
    def _on_click(self, index: int):
        """Handle mouse click on item."""
        self.selected_index = index
        self.select_current()
    
    def _on_hover(self, index: int):
        """Handle mouse hover on item."""
        if index != self.selected_index:
            self.selected_index = index
            self._update_selection()


if __name__ == "__main__":
    # Test overlay
    logging.basicConfig(level=logging.DEBUG)
    
    def on_select(movie):
        print(f"Selected: {movie}")
    
    def on_close():
        print("Overlay closed")
    
    overlay = SuggestionOverlay(on_select=on_select, on_close=on_close)
    overlay.start()
    
    # Wait a moment for initialization
    import time
    time.sleep(1)
    
    # Test data
    test_movies = [
        {"title": "The Conjuring", "year": 2013, "rating": 7.5, "genres": ["horror", "thriller"]},
        {"title": "Hereditary", "year": 2018, "rating": 7.3, "genres": ["horror", "drama"]},
        {"title": "Get Out", "year": 2017, "rating": 7.7, "genres": ["horror", "mystery"]},
        {"title": "A Quiet Place", "year": 2018, "rating": 7.5, "genres": ["horror", "sci-fi"]},
        {"title": "It", "year": 2017, "rating": 7.3, "genres": ["horror", "thriller"]},
    ]
    
    overlay.show(test_movies, "horror movies")
    
    print("Overlay shown. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        overlay.stop()
