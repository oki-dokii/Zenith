"""
Netflix AI Assistant - Simple Hotkey Version

This version uses a global hotkey (Ctrl+Space) to trigger the overlay
instead of monitoring keyboard input inside Netflix.

More reliable with UWP apps like Netflix.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard  # Using 'keyboard' library for global hotkeys
import json
import os
from pathlib import Path

# Configuration
HOTKEY = 'ctrl+space'  # Press Ctrl+Space to show overlay
MOVIES_JSON = os.path.join(os.path.dirname(__file__), 'data', 'movies.json')

# Colors (Netflix theme)
BG_COLOR = '#141414'
FG_COLOR = '#ffffff'
HIGHLIGHT_COLOR = '#e50914'
SECONDARY_COLOR = '#333333'


class MovieDatabase:
    """Simple movie search."""
    
    GENRE_MAP = {
        'horror': ['horror', 'scary', 'creepy', 'terrifying'],
        'comedy': ['comedy', 'funny', 'hilarious', 'laugh'],
        'action': ['action', 'explosive', 'fight', 'exciting'],
        'sci-fi': ['sci-fi', 'scifi', 'space', 'future', 'futuristic'],
        'romance': ['romance', 'romantic', 'love'],
        'drama': ['drama', 'emotional', 'serious'],
        'thriller': ['thriller', 'suspense', 'tense'],
        'mystery': ['mystery', 'detective', 'whodunit'],
        'animation': ['animation', 'animated', 'cartoon', 'anime'],
        'superhero': ['superhero', 'marvel', 'dc', 'heroes'],
    }
    
    def __init__(self):
        self.movies = []
        self._load()
    
    def _load(self):
        try:
            with open(MOVIES_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.movies = data.get('movies', [])
        except Exception as e:
            print(f"Error loading movies: {e}")
            self.movies = []
    
    def search(self, query: str, limit: int = 8):
        if not query.strip():
            # Return top-rated movies
            sorted_movies = sorted(self.movies, key=lambda m: m.get('rating', 0), reverse=True)
            return sorted_movies[:limit]
        
        query_lower = query.lower()
        results = []
        
        # Find matching genres
        target_genres = set()
        for genre, keywords in self.GENRE_MAP.items():
            for kw in keywords:
                if kw in query_lower:
                    target_genres.add(genre)
        
        for movie in self.movies:
            score = 0
            movie_genres = [g.lower() for g in movie.get('genres', [])]
            title = movie.get('title', '').lower()
            
            # Genre match
            for g in target_genres:
                if g in movie_genres:
                    score += 10
            
            # Title match
            if query_lower in title:
                score += 20
            
            if score > 0:
                results.append((movie, score))
        
        results.sort(key=lambda x: (x[1], x[0].get('rating', 0)), reverse=True)
        return [m for m, s in results[:limit]]


class SimpleOverlay:
    """Simple floating overlay window."""
    
    def __init__(self):
        self.root = None
        self.db = MovieDatabase()
        self.is_visible = False
        self.selected_index = 0
        self.current_results = []
        self._create_window()
    
    def _create_window(self):
        self.root = tk.Tk()
        self.root.title("Netflix AI Assistant")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg=BG_COLOR)
        
        # Center on screen
        width, height = 450, 500
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header
        header = tk.Frame(main, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            header, text="🎬 Netflix AI Assistant",
            font=('Segoe UI', 14, 'bold'),
            fg=HIGHLIGHT_COLOR, bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header, text="Press ESC to close",
            font=('Segoe UI', 9),
            fg='#666666', bg=BG_COLOR
        ).pack(side=tk.RIGHT)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        search_frame = tk.Frame(main, bg=SECONDARY_COLOR)
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 12),
            bg=SECONDARY_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.search_entry.pack(fill=tk.X, padx=10, pady=10)
        self.search_entry.insert(0, "Type to search (e.g., horror, comedy, sci-fi)...")
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        
        # Results frame
        self.results_frame = tk.Frame(main, bg=BG_COLOR)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Instructions
        inst = tk.Frame(main, bg=BG_COLOR)
        inst.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            inst, text="↑↓ Navigate  |  Enter Select  |  ESC Close",
            font=('Segoe UI', 9),
            fg='#666666', bg=BG_COLOR
        ).pack()
        
        # Bindings
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<Return>', lambda e: self._select_current())
        self.root.bind('<Up>', lambda e: self._navigate(-1))
        self.root.bind('<Down>', lambda e: self._navigate(1))
        
        # Start hidden
        self.root.withdraw()
        
        # Show initial results
        self._update_results(self.db.search('', 8))
    
    def _on_focus_in(self, event):
        if self.search_entry.get().startswith("Type to search"):
            self.search_entry.delete(0, tk.END)
    
    def _on_search_change(self, *args):
        query = self.search_var.get()
        if query.startswith("Type to search"):
            return
        results = self.db.search(query, 8)
        self._update_results(results)
    
    def _update_results(self, results):
        self.current_results = results
        self.selected_index = 0
        
        # Clear existing
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not results:
            tk.Label(
                self.results_frame, text="No results found",
                font=('Segoe UI', 11),
                fg='#666666', bg=BG_COLOR
            ).pack(pady=20)
            return
        
        self.result_frames = []
        for i, movie in enumerate(results):
            frame = self._create_result_item(i, movie)
            self.result_frames.append(frame)
        
        self._highlight_selected()
    
    def _create_result_item(self, index, movie):
        frame = tk.Frame(self.results_frame, bg=BG_COLOR, cursor='hand2')
        frame.pack(fill=tk.X, pady=3)
        
        inner = tk.Frame(frame, bg=SECONDARY_COLOR)
        inner.pack(fill=tk.X, padx=0, pady=0)
        
        # Title
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        rating = movie.get('rating', 'N/A')
        genres = movie.get('genres', [])[:3]
        
        title_label = tk.Label(
            inner, text=f"{title} ({year})",
            font=('Segoe UI', 11, 'bold'),
            fg=FG_COLOR, bg=SECONDARY_COLOR,
            anchor='w'
        )
        title_label.pack(fill=tk.X, padx=12, pady=(8, 2))
        
        meta = f"★ {rating}  |  {' • '.join(g.capitalize() for g in genres)}"
        meta_label = tk.Label(
            inner, text=meta,
            font=('Segoe UI', 9),
            fg='#999999', bg=SECONDARY_COLOR,
            anchor='w'
        )
        meta_label.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        # Click binding
        for widget in [frame, inner, title_label, meta_label]:
            widget.bind('<Button-1>', lambda e, idx=index: self._select(idx))
            widget.bind('<Enter>', lambda e, idx=index: self._hover(idx))
        
        frame.inner = inner
        frame.movie = movie
        return frame
    
    def _highlight_selected(self):
        for i, frame in enumerate(self.result_frames):
            if i == self.selected_index:
                frame.inner.configure(bg=HIGHLIGHT_COLOR)
                for child in frame.inner.winfo_children():
                    child.configure(bg=HIGHLIGHT_COLOR)
            else:
                frame.inner.configure(bg=SECONDARY_COLOR)
                for child in frame.inner.winfo_children():
                    child.configure(bg=SECONDARY_COLOR)
    
    def _navigate(self, direction):
        if self.current_results:
            self.selected_index = (self.selected_index + direction) % len(self.current_results)
            self._highlight_selected()
    
    def _hover(self, index):
        self.selected_index = index
        self._highlight_selected()
    
    def _select(self, index):
        self.selected_index = index
        self._select_current()
    
    def _select_current(self):
        if self.current_results and 0 <= self.selected_index < len(self.current_results):
            movie = self.current_results[self.selected_index]
            title = movie.get('title', '')
            print(f"Selected: {title}")
            
            # Hide overlay
            self.hide()
            
            # Type the title (after a short delay to let Netflix get focus)
            if title:
                time.sleep(0.3)
                keyboard.write(title, delay=0.02)
                time.sleep(0.1)
                keyboard.press_and_release('enter')
    
    def show(self):
        if not self.is_visible:
            self.is_visible = True
            self.search_var.set('')
            self._update_results(self.db.search('', 8))
            
            # Center on screen
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.search_entry.focus_set()
    
    def hide(self):
        if self.is_visible:
            self.is_visible = False
            self.root.withdraw()
    
    def toggle(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def run(self):
        self.root.mainloop()


def main():
    print("=" * 50)
    print("Netflix AI Assistant - Simple Version")
    print("=" * 50)
    print()
    print(f"Press {HOTKEY.upper()} to open the assistant")
    print("Then search for movies and press Enter to select")
    print()
    print("Press Ctrl+C to quit")
    print("=" * 50)
    
    overlay = SimpleOverlay()
    
    # Register global hotkey
    keyboard.add_hotkey(HOTKEY, overlay.toggle)
    
    # Run the overlay
    overlay.run()


if __name__ == "__main__":
    main()
