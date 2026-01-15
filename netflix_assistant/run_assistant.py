"""
Netflix AI Assistant - Simple & Reliable Version
Press F2 to open/close the assistant
"""

import tkinter as tk
import threading
import time
import json
import os
import requests

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_JSON = os.path.join(SCRIPT_DIR, 'data', 'movies.json')

# Gemini API
GEMINI_URL = "https://gemini-pro-ai.p.rapidapi.com/"
GEMINI_HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": "gemini-pro-ai.p.rapidapi.com",
    "x-rapidapi-key": "9539ea1afamshabf76de03e0583fp19a33ajsn7d78d38374bc"
}

# Colors
BG = '#141414'
FG = '#ffffff'
RED = '#e50914'
GRAY = '#333333'
TEAL = '#00d4aa'


def load_movies():
    try:
        with open(MOVIES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f).get('movies', [])
    except:
        return []


def ask_gemini(query, movies):
    """Ask Gemini for movie recommendations."""
    movie_list = ", ".join([f"{m['title']} ({m['year']})" for m in movies])
    
    prompt = f"""From this movie list: {movie_list}

Recommend 5-8 movies for: "{query}"

Respond with ONLY a JSON array of titles. Example: ["Movie 1", "Movie 2"]"""

    try:
        response = requests.post(
            GEMINI_URL,
            headers=GEMINI_HEADERS,
            json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            # Extract JSON array
            import re
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        return []
    except Exception as e:
        print(f"API Error: {e}")
        return []


class NetflixAssistant:
    def __init__(self):
        self.movies = load_movies()
        self.root = tk.Tk()
        self.root.title("Netflix AI")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=BG)
        
        # Size and position
        w, h = 480, 520
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        self.selected = 0
        self.results = []
        self.result_widgets = []
        
        self._build_ui()
        self.root.bind('<F2>', lambda e: self.root.withdraw())
        self.root.bind('<Escape>', lambda e: self.root.withdraw())
        
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill='x', padx=15, pady=10)
        tk.Label(hdr, text="🤖 Netflix AI Assistant", font=('Segoe UI', 14, 'bold'), fg=TEAL, bg=BG).pack(side='left')
        tk.Label(hdr, text="ESC/F2 to close", font=('Segoe UI', 9), fg='#666', bg=BG).pack(side='right')
        
        # Search box
        sf = tk.Frame(self.root, bg=GRAY)
        sf.pack(fill='x', padx=15, pady=5)
        
        self.entry = tk.Entry(sf, font=('Segoe UI', 12), bg=GRAY, fg=FG, insertbackground=FG, relief='flat')
        self.entry.pack(fill='x', padx=10, pady=10)
        self.entry.bind('<Return>', self._on_search)
        
        # Hint
        tk.Label(self.root, text="Type a query and press Enter (e.g., 'scary but fun')", 
                 font=('Segoe UI', 9), fg='#888', bg=BG).pack(pady=5)
        
        # Status
        self.status = tk.Label(self.root, text="", font=('Segoe UI', 10), fg=TEAL, bg=BG)
        self.status.pack()
        
        # Results area
        self.results_frame = tk.Frame(self.root, bg=BG)
        self.results_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Footer
        tk.Label(self.root, text="↑↓ Navigate  |  Enter/Click Select", 
                 font=('Segoe UI', 9), fg='#666', bg=BG).pack(pady=5)
        
        # Key bindings
        self.root.bind('<Up>', lambda e: self._nav(-1))
        self.root.bind('<Down>', lambda e: self._nav(1))
        self.entry.bind('<Up>', lambda e: self._nav(-1))
        self.entry.bind('<Down>', lambda e: self._nav(1))
    
    def _on_search(self, event=None):
        query = self.entry.get().strip()
        if not query:
            return
        
        self.status.config(text="🔄 AI is thinking...")
        self.root.update()
        
        # Run in background
        def fetch():
            titles = ask_gemini(query, self.movies)
            results = []
            for t in titles:
                for m in self.movies:
                    if t.lower() in m.get('title', '').lower():
                        results.append(m)
                        break
            self.root.after(0, lambda: self._show_results(results))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _show_results(self, results):
        self.status.config(text="")
        self.results = results
        self.selected = 0
        
        # Clear old
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.result_widgets = []
        
        if not results:
            tk.Label(self.results_frame, text="No results. Try different words!", 
                     font=('Segoe UI', 11), fg='#666', bg=BG).pack(pady=20)
            return
        
        for i, movie in enumerate(results[:8]):
            frame = tk.Frame(self.results_frame, bg=GRAY, cursor='hand2')
            frame.pack(fill='x', pady=2)
            
            title = f"{movie.get('title', '?')} ({movie.get('year', '')})"
            genres = ' • '.join(movie.get('genres', [])[:3])
            rating = movie.get('rating', 'N/A')
            
            lbl1 = tk.Label(frame, text=title, font=('Segoe UI', 11, 'bold'), fg=FG, bg=GRAY, anchor='w')
            lbl1.pack(fill='x', padx=10, pady=(6, 0))
            
            lbl2 = tk.Label(frame, text=f"★ {rating}  |  {genres}", font=('Segoe UI', 9), fg='#999', bg=GRAY, anchor='w')
            lbl2.pack(fill='x', padx=10, pady=(0, 6))
            
            # Click handler
            for w in [frame, lbl1, lbl2]:
                w.bind('<Button-1>', lambda e, idx=i: self._select(idx))
            
            self.result_widgets.append((frame, lbl1, lbl2))
        
        self._highlight()
    
    def _nav(self, direction):
        if self.results:
            self.selected = (self.selected + direction) % len(self.results)
            self._highlight()
    
    def _highlight(self):
        for i, (frame, lbl1, lbl2) in enumerate(self.result_widgets):
            color = RED if i == self.selected else GRAY
            frame.config(bg=color)
            lbl1.config(bg=color)
            lbl2.config(bg=color)
    
    def _select(self, idx):
        if 0 <= idx < len(self.results):
            movie = self.results[idx]
            title = movie.get('title', '')
            print(f"Selected: {title}")
            
            self.root.withdraw()
            
            # Type the title using pyautogui for reliability
            try:
                import pyautogui
                time.sleep(0.3)
                pyautogui.typewrite(title, interval=0.02)
                time.sleep(0.1)
                pyautogui.press('enter')
            except ImportError:
                # Fallback - copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(title)
                print(f"Copied to clipboard: {title}")
                print("Paste with Ctrl+V in Netflix!")
    
    def show(self):
        self.entry.delete(0, 'end')
        self.status.config(text="")
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.result_widgets = []
        self.results = []
        
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()
    
    def run(self):
        # Register F2 global hotkey
        def check_f2():
            import ctypes
            VK_F2 = 0x71
            while True:
                # Check if F2 is pressed (async)
                if ctypes.windll.user32.GetAsyncKeyState(VK_F2) & 0x8000:
                    self.root.after(0, self.show)
                    time.sleep(0.3)  # Debounce
                time.sleep(0.05)
        
        threading.Thread(target=check_f2, daemon=True).start()
        
        print("=" * 50)
        print("🤖 Netflix AI Assistant")
        print("=" * 50)
        print()
        print("Press F2 to open the assistant!")
        print("Then type your query and press Enter.")
        print()
        print("Examples:")
        print("  'scary but not too gory'")
        print("  'feel-good comedy'")
        print("  'movies like Inception'")
        print()
        print("Press Ctrl+C to quit")
        print("=" * 50)
        
        self.root.withdraw()  # Start hidden
        self.root.mainloop()


if __name__ == "__main__":
    app = NetflixAssistant()
    app.run()
