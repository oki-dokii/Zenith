"""
Netflix AI Assistant - AI-Powered Version with Gemini

Uses Google Gemini via RapidAPI for intelligent movie recommendations.
Press Ctrl+Space to open, type natural language queries like:
- "something scary but not too gory"
- "feel-good movies for a rainy day"
- "movies like Inception"
"""

import tkinter as tk
import threading
import time
import keyboard
import json
import os
import requests
from pathlib import Path

# Configuration
HOTKEY = 'ctrl+space'
MOVIES_JSON = os.path.join(os.path.dirname(__file__), 'data', 'movies.json')

# Gemini API Configuration (RapidAPI)
GEMINI_API_URL = "https://gemini-pro-ai.p.rapidapi.com/"
GEMINI_HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": "gemini-pro-ai.p.rapidapi.com",
    "x-rapidapi-key": "9539ea1afamshabf76de03e0583fp19a33ajsn7d78d38374bc"
}

# Colors (Netflix theme)
BG_COLOR = '#141414'
FG_COLOR = '#ffffff'
HIGHLIGHT_COLOR = '#e50914'
SECONDARY_COLOR = '#333333'
AI_COLOR = '#00d4aa'


class MovieDatabase:
    """Movie database with titles for AI to choose from."""
    
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
    
    def get_all_titles(self):
        """Get all movie titles for AI context."""
        return [m.get('title', '') for m in self.movies]
    
    def get_movie_by_title(self, title):
        """Find movie by title (case-insensitive)."""
        title_lower = title.lower().strip()
        for movie in self.movies:
            if movie.get('title', '').lower() == title_lower:
                return movie
        # Partial match
        for movie in self.movies:
            if title_lower in movie.get('title', '').lower():
                return movie
        return None
    
    def get_movies_by_titles(self, titles):
        """Get full movie data for a list of titles."""
        results = []
        for title in titles:
            movie = self.get_movie_by_title(title)
            if movie:
                results.append(movie)
        return results


class GeminiAI:
    """Gemini AI integration for movie recommendations."""
    
    def __init__(self, movie_db: MovieDatabase):
        self.movie_db = movie_db
        self.conversation_history = []
    
    def get_recommendations(self, query: str) -> list:
        """Get AI-powered movie recommendations."""
        
        # Build the movie list context
        all_titles = self.movie_db.get_all_titles()
        movies_context = "\n".join([
            f"- {m.get('title')} ({m.get('year')}) - {', '.join(m.get('genres', []))} - Rating: {m.get('rating')}"
            for m in self.movie_db.movies
        ])
        
        # System prompt
        system_prompt = f"""You are a movie recommendation assistant. You have access to this movie catalog:

{movies_context}

When the user asks for movie recommendations, respond ONLY with a JSON array of movie titles from the catalog above. Choose 5-8 relevant movies.

Example response format:
["The Conjuring", "Hereditary", "Get Out"]

Only respond with movies from the catalog. Only output the JSON array, nothing else."""

        # User query
        user_message = f"Recommend movies for: {query}"
        
        try:
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I will only respond with JSON arrays of movie titles from the catalog."}]},
                    {"role": "user", "parts": [{"text": user_message}]}
                ]
            }
            
            response = requests.post(
                GEMINI_API_URL,
                headers=GEMINI_HEADERS,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Parse the response to extract movie titles
                ai_text = self._extract_text(data)
                titles = self._parse_titles(ai_text)
                return self.movie_db.get_movies_by_titles(titles)
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return []
    
    def _extract_text(self, response_data):
        """Extract text from Gemini response."""
        try:
            # RapidAPI Gemini response format
            if isinstance(response_data, dict):
                candidates = response_data.get('candidates', [])
                if candidates:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
            return str(response_data)
        except Exception:
            return str(response_data)
    
    def _parse_titles(self, text):
        """Parse movie titles from AI response."""
        try:
            # Try to find JSON array in the response
            import re
            # Find anything that looks like a JSON array
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                titles = json.loads(match.group())
                if isinstance(titles, list):
                    return [str(t).strip() for t in titles if t]
        except Exception as e:
            print(f"Parse error: {e}")
        
        # Fallback: try to extract quoted strings
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[:8]
        
        return []


class AIOverlay:
    """AI-powered floating overlay window."""
    
    def __init__(self):
        self.root = None
        self.db = MovieDatabase()
        self.ai = GeminiAI(self.db)
        self.is_visible = False
        self.selected_index = 0
        self.current_results = []
        self.loading = False
        self._create_window()
    
    def _create_window(self):
        self.root = tk.Tk()
        self.root.title("Netflix AI Assistant")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg=BG_COLOR)
        
        # Center on screen
        width, height = 500, 550
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
            header, text="🤖 Netflix AI Assistant",
            font=('Segoe UI', 14, 'bold'),
            fg=AI_COLOR, bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header, text="Powered by Gemini",
            font=('Segoe UI', 9),
            fg='#666666', bg=BG_COLOR
        ).pack(side=tk.RIGHT)
        
        # Search entry
        self.search_var = tk.StringVar()
        
        search_frame = tk.Frame(main, bg=SECONDARY_COLOR)
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        
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
        self.search_entry.insert(0, "Ask anything... (e.g., 'scary but not too gory')")
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        self.search_entry.bind('<Return>', self._on_search)
        
        # AI hint
        hint = tk.Label(
            main, text="Press Enter to get AI recommendations",
            font=('Segoe UI', 9),
            fg='#888888', bg=BG_COLOR
        )
        hint.pack(pady=(0, 10))
        
        # Loading label
        self.loading_label = tk.Label(
            main, text="",
            font=('Segoe UI', 10),
            fg=AI_COLOR, bg=BG_COLOR
        )
        self.loading_label.pack()
        
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
        self.root.bind('<Up>', lambda e: self._navigate(-1))
        self.root.bind('<Down>', lambda e: self._navigate(1))
        
        # Start hidden
        self.root.withdraw()
    
    def _on_focus_in(self, event):
        current = self.search_entry.get()
        if current.startswith("Ask anything"):
            self.search_entry.delete(0, tk.END)
    
    def _on_search(self, event=None):
        query = self.search_var.get().strip()
        if not query or query.startswith("Ask anything"):
            return
        
        # Show loading
        self.loading = True
        self.loading_label.config(text="🔄 AI is thinking...")
        self.root.update()
        
        # Get AI recommendations in background
        def fetch():
            results = self.ai.get_recommendations(query)
            self.root.after(0, lambda: self._show_results(results))
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
    
    def _show_results(self, results):
        self.loading = False
        self.loading_label.config(text="")
        self.current_results = results
        self.selected_index = 0
        
        # Clear existing
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not results:
            tk.Label(
                self.results_frame, text="No recommendations found. Try a different query!",
                font=('Segoe UI', 11),
                fg='#666666', bg=BG_COLOR
            ).pack(pady=20)
            return
        
        # AI response header
        tk.Label(
            self.results_frame, text=f"🎬 AI Recommendations ({len(results)} movies)",
            font=('Segoe UI', 10, 'bold'),
            fg=AI_COLOR, bg=BG_COLOR, anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.result_frames = []
        for i, movie in enumerate(results):
            frame = self._create_result_item(i, movie)
            self.result_frames.append(frame)
        
        self._highlight_selected()
    
    def _create_result_item(self, index, movie):
        frame = tk.Frame(self.results_frame, bg=BG_COLOR, cursor='hand2')
        frame.pack(fill=tk.X, pady=2)
        
        inner = tk.Frame(frame, bg=SECONDARY_COLOR)
        inner.pack(fill=tk.X)
        
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        rating = movie.get('rating', 'N/A')
        genres = movie.get('genres', [])[:3]
        
        title_label = tk.Label(
            inner, text=f"{title} ({year})",
            font=('Segoe UI', 11, 'bold'),
            fg=FG_COLOR, bg=SECONDARY_COLOR, anchor='w'
        )
        title_label.pack(fill=tk.X, padx=12, pady=(6, 1))
        
        meta = f"★ {rating}  |  {' • '.join(g.capitalize() for g in genres)}"
        meta_label = tk.Label(
            inner, text=meta,
            font=('Segoe UI', 9),
            fg='#999999', bg=SECONDARY_COLOR, anchor='w'
        )
        meta_label.pack(fill=tk.X, padx=12, pady=(0, 6))
        
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
        if self.current_results and 0 <= index < len(self.current_results):
            movie = self.current_results[index]
            title = movie.get('title', '')
            print(f"Selected: {title}")
            
            self.hide()
            
            if title:
                time.sleep(0.3)
                keyboard.write(title, delay=0.02)
                time.sleep(0.1)
                keyboard.press_and_release('enter')
    
    def show(self):
        if not self.is_visible:
            self.is_visible = True
            self.search_var.set('')
            self.current_results = []
            self.loading_label.config(text="")
            
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.search_entry.focus_set()
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Ask anything... (e.g., 'scary but not too gory')")
    
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
    print("=" * 60)
    print("🤖 Netflix AI Assistant - Powered by Gemini")
    print("=" * 60)
    print()
    print(f"Press {HOTKEY.upper()} to open the AI assistant")
    print()
    print("Example queries:")
    print("  • 'scary movies but not too gory'")
    print("  • 'feel-good comedy for a rainy day'")
    print("  • 'movies like Inception'")
    print("  • 'something romantic and emotional'")
    print()
    print("Press Ctrl+C to quit")
    print("=" * 60)
    
    overlay = AIOverlay()
    keyboard.add_hotkey(HOTKEY, overlay.toggle)
    overlay.run()


if __name__ == "__main__":
    main()
