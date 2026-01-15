"""
Search Engine Module

Handles query parsing and movie search functionality.
Uses fuzzy matching to find relevant movies based on genre or title.
"""

import json
import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

from .config import MOVIES_JSON, DEMO_MODE

logger = logging.getLogger(__name__)


class MovieSearchEngine:
    """
    Search engine for finding movies based on user queries.
    """
    
    # Common search terms mapped to genres
    GENRE_MAPPINGS = {
        # Horror
        'horror': ['horror'],
        'scary': ['horror', 'thriller'],
        'creepy': ['horror', 'thriller'],
        'spooky': ['horror'],
        'terrifying': ['horror'],
        'hor': ['horror'],
        
        # Comedy
        'comedy': ['comedy'],
        'funny': ['comedy'],
        'hilarious': ['comedy'],
        'laugh': ['comedy'],
        'com': ['comedy'],
        
        # Action
        'action': ['action'],
        'explosive': ['action'],
        'fight': ['action'],
        'exciting': ['action', 'thriller'],
        'act': ['action'],
        
        # Drama
        'drama': ['drama'],
        'emotional': ['drama'],
        'moving': ['drama'],
        'serious': ['drama'],
        'dra': ['drama'],
        
        # Sci-Fi
        'sci-fi': ['sci-fi'],
        'scifi': ['sci-fi'],
        'science fiction': ['sci-fi'],
        'space': ['sci-fi'],
        'future': ['sci-fi'],
        'futuristic': ['sci-fi'],
        'sci': ['sci-fi'],
        
        # Romance
        'romance': ['romance'],
        'romantic': ['romance'],
        'love': ['romance'],
        'love story': ['romance'],
        'rom': ['romance'],
        
        # Thriller
        'thriller': ['thriller'],
        'suspense': ['thriller'],
        'tense': ['thriller'],
        'suspenseful': ['thriller'],
        'thrill': ['thriller'],
        
        # Mystery
        'mystery': ['mystery'],
        'mysterious': ['mystery'],
        'detective': ['mystery', 'crime'],
        'whodunit': ['mystery'],
        'myst': ['mystery'],
        
        # Superhero
        'superhero': ['superhero'],
        'marvel': ['superhero', 'action'],
        'dc': ['superhero', 'action'],
        'heroes': ['superhero'],
        'super': ['superhero'],
        
        # Animation
        'animation': ['animation'],
        'animated': ['animation'],
        'cartoon': ['animation'],
        'anime': ['anime', 'animation'],
        'anim': ['animation'],
        
        # Classic
        'classic': ['classic'],
        'old': ['classic'],
        'vintage': ['classic'],
        
        # Family
        'family': ['family'],
        'kids': ['family', 'animation'],
        'children': ['family'],
        'fam': ['family'],
        
        # Crime
        'crime': ['crime'],
        'criminal': ['crime'],
        'mafia': ['crime', 'drama'],
        'gangster': ['crime'],
        'cri': ['crime'],
        
        # Adventure
        'adventure': ['adventure'],
        'adv': ['adventure'],
        'journey': ['adventure'],
        'quest': ['adventure'],
        
        # Documentary
        'documentary': ['documentary'],
        'doc': ['documentary'],
        'docu': ['documentary'],
        'true story': ['documentary', 'drama'],
    }
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the search engine.
        
        Args:
            data_path: Path to movies JSON file (uses default if not specified)
        """
        self.data_path = data_path or MOVIES_JSON
        self.movies: List[Dict] = []
        self._load_movies()
    
    def _load_movies(self):
        """Load movies from JSON file."""
        try:
            path = Path(self.data_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.movies = data.get('movies', [])
                    logger.info(f"Loaded {len(self.movies)} movies from {self.data_path}")
            else:
                logger.warning(f"Movies file not found: {self.data_path}")
                self.movies = []
        except Exception as e:
            logger.error(f"Error loading movies: {e}")
            self.movies = []
    
    def search(self, query: str, max_results: int = 8) -> List[Dict]:
        """
        Search for movies matching the query.
        
        Args:
            query: User's search query (after AI: prefix)
            max_results: Maximum number of results to return
        
        Returns:
            List of matching movies (dictionaries)
        """
        if not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        # Parse genres from query
        target_genres = self._extract_genres(query_lower)
        
        # Extract potential title keywords
        title_keywords = self._extract_title_keywords(query_lower)
        
        logger.debug(f"Searching with genres={target_genres}, keywords={title_keywords}")
        
        for movie in self.movies:
            score = self._calculate_match_score(movie, target_genres, title_keywords, query_lower)
            if score > 0:
                results.append((movie, score))
        
        # Sort by score (descending), then by rating (descending)
        results.sort(key=lambda x: (x[1], x[0].get('rating', 0)), reverse=True)
        
        # If no results, fallback to title prefix matching or top movies
        if not results:
            # Try prefix matching on title
            for movie in self.movies:
                title = movie.get('title', '').lower()
                # Match if title starts with query or any word in title starts with query
                words = title.split()
                if title.startswith(query_lower) or any(w.startswith(query_lower) for w in words):
                    score = 10.0 + movie.get('rating', 5.0)
                    results.append((movie, score))
            
            results.sort(key=lambda x: x[1], reverse=True)
        
        # If still no results, return top-rated movies
        if not results:
            top_movies = sorted(self.movies, key=lambda m: m.get('rating', 0), reverse=True)
            return top_movies[:max_results]
        
        # Return top results
        return [movie for movie, score in results[:max_results]]
    
    def _extract_genres(self, query: str) -> List[str]:
        """Extract genre terms from the query."""
        genres = set()
        
        for term, mapped_genres in self.GENRE_MAPPINGS.items():
            if term in query:
                genres.update(mapped_genres)
        
        return list(genres)
    
    def _extract_title_keywords(self, query: str) -> List[str]:
        """Extract potential title keywords from the query."""
        # Remove common words and genre terms
        stopwords = {
            'a', 'an', 'the', 'movie', 'movies', 'film', 'films', 'show', 'shows',
            'good', 'best', 'great', 'top', 'popular', 'new', 'old', 'like',
            'similar', 'to', 'with', 'about', 'for', 'me', 'recommend', 'suggestion',
            'suggestions', 'find', 'search', 'get', 'want', 'looking'
        }
        
        # Add genre terms to stopwords
        for term in self.GENRE_MAPPINGS.keys():
            stopwords.add(term)
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
    
    def _calculate_match_score(
        self, 
        movie: Dict, 
        target_genres: List[str], 
        title_keywords: List[str],
        full_query: str
    ) -> float:
        """
        Calculate match score for a movie.
        
        Args:
            movie: Movie dict
            target_genres: List of target genres
            title_keywords: List of title keywords to match
            full_query: The full query string
        
        Returns:
            Match score (0 = no match, higher = better match)
        """
        score = 0.0
        movie_genres = [g.lower() for g in movie.get('genres', [])]
        movie_title = movie.get('title', '').lower()
        movie_desc = movie.get('description', '').lower()
        
        # Genre matching (high weight)
        for genre in target_genres:
            if genre in movie_genres:
                score += 10.0
        
        # Title keyword matching
        for keyword in title_keywords:
            if keyword in movie_title:
                score += 15.0
            elif keyword in movie_desc:
                score += 3.0
        
        # Exact title match (highest priority)
        if full_query in movie_title:
            score += 50.0
        
        # Boost by rating (slight preference for higher-rated movies)
        if score > 0:
            rating = movie.get('rating', 5.0)
            score += rating * 0.5
        
        return score
    
    def get_suggestions_for_category(self, category: str, max_results: int = 8) -> List[Dict]:
        """
        Get movie suggestions for a specific category/genre.
        
        Args:
            category: Genre category
            max_results: Maximum results to return
        
        Returns:
            List of movies in that category
        """
        category_lower = category.lower()
        target_genres = self.GENRE_MAPPINGS.get(category_lower, [category_lower])
        
        results = []
        for movie in self.movies:
            movie_genres = [g.lower() for g in movie.get('genres', [])]
            if any(g in movie_genres for g in target_genres):
                results.append(movie)
        
        # Sort by rating
        results.sort(key=lambda m: m.get('rating', 0), reverse=True)
        
        return results[:max_results]
    
    def get_all_genres(self) -> List[str]:
        """Get list of all unique genres in the dataset."""
        genres = set()
        for movie in self.movies:
            genres.update(movie.get('genres', []))
        return sorted(genres)
    
    def search_with_genres(self, query: str, max_genres: int = 3, max_movies: int = 5) -> Dict:
        """
        Search for both matching genres and movies.
        
        Args:
            query: User's search query (after AI: prefix)
            max_genres: Maximum number of genre suggestions to return
            max_movies: Maximum number of movie suggestions to return
        
        Returns:
            Dict with 'genres' and 'movies' lists
        """
        matching_genres = self._get_matching_genres(query)
        movies = self.search(query, max_results=max_movies)
        
        return {
            'genres': matching_genres[:max_genres],
            'movies': movies
        }
    
    def _get_matching_genres(self, query: str) -> List[Dict]:
        """
        Get genres that match the query keyword.
        
        Args:
            query: User's search query
        
        Returns:
            List of genre dicts with 'name', 'icon', and 'keywords'
        """
        query_lower = query.lower().strip()
        matching = []
        
        # Genre icons for display
        GENRE_ICONS = {
            'horror': '👻',
            'comedy': '😂',
            'action': '💥',
            'drama': '🎭',
            'sci-fi': '🚀',
            'romance': '❤️',
            'thriller': '😱',
            'mystery': '🔍',
            'superhero': '🦸',
            'animation': '🎨',
            'anime': '🎌',
            'classic': '🎬',
            'family': '👨‍👩‍👧‍👦',
            'crime': '🔫',
            'adventure': '🗺️',
            'documentary': '📹',
        }
        
        # Find genres that match the query
        seen_genres = set()
        query_words = query_lower.split()
        
        for term, mapped_genres in self.GENRE_MAPPINGS.items():
            # Check if term is in query or matches any word
            if term in query_lower or any(w.startswith(term) or term.startswith(w) for w in query_words if len(w) >= 2):
                for genre in mapped_genres:
                    if genre not in seen_genres:
                        seen_genres.add(genre)
                        matching.append({
                            'name': genre.capitalize(),
                            'icon': GENRE_ICONS.get(genre, '🎬'),
                            'search_term': genre
                        })
        
        return matching


# Singleton instance
_search_engine = None

def get_search_engine() -> MovieSearchEngine:
    """Get or create the singleton search engine instance."""
    global _search_engine
    if _search_engine is None:
        _search_engine = MovieSearchEngine()
    return _search_engine


if __name__ == "__main__":
    # Test search engine
    logging.basicConfig(level=logging.DEBUG)
    
    engine = MovieSearchEngine()
    
    print(f"Loaded {len(engine.movies)} movies")
    print(f"Genres: {engine.get_all_genres()}")
    print()
    
    # Test searches
    test_queries = [
        "horror movies",
        "funny comedy",
        "sci-fi space",
        "romantic love story",
        "action thriller",
        "The Conjuring",
        "superhero marvel",
        "anime animation",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = engine.search(query)
        for i, movie in enumerate(results[:5], 1):
            print(f"   {i}. {movie['title']} ({movie['year']}) ★{movie['rating']}")
