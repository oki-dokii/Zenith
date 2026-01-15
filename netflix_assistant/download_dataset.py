"""
Generate a comprehensive movie database for Netflix AI Assistant.
Uses a curated list of popular movies organized by genre.
"""
import json
import os
import random

# Comprehensive movie database organized by genre
MOVIES_BY_GENRE = {
    "horror": [
        ("The Conjuring", 2013, 7.5), ("The Conjuring 2", 2016, 7.3), ("Annabelle", 2014, 5.4),
        ("Hereditary", 2018, 7.3), ("Midsommar", 2019, 7.1), ("Get Out", 2017, 7.7),
        ("Us", 2019, 6.8), ("A Quiet Place", 2018, 7.5), ("A Quiet Place Part II", 2020, 7.3),
        ("It", 2017, 7.3), ("It Chapter Two", 2019, 6.5), ("The Shining", 1980, 8.4),
        ("The Exorcist", 1973, 8.1), ("Insidious", 2010, 6.8), ("Insidious: Chapter 2", 2013, 6.6),
        ("Sinister", 2012, 6.8), ("Paranormal Activity", 2007, 6.3), ("The Ring", 2002, 7.1),
        ("The Grudge", 2004, 5.9), ("Saw", 2004, 7.6), ("Halloween", 1978, 7.7),
        ("Halloween", 2018, 6.5), ("A Nightmare on Elm Street", 1984, 7.5), ("Scream", 1996, 7.4),
        ("Scream", 2022, 6.4), ("The Texas Chain Saw Massacre", 1974, 7.4), ("The Babadook", 2014, 6.8),
        ("Candyman", 1992, 6.6), ("Candyman", 2021, 6.1), ("The Witch", 2015, 6.9),
        ("The Lighthouse", 2019, 7.5), ("Doctor Sleep", 2019, 7.3), ("Bird Box", 2018, 6.6),
        ("Don't Breathe", 2016, 7.1), ("The Invisible Man", 2020, 7.1), ("Ready or Not", 2019, 6.9),
        ("Pearl", 2022, 7.0), ("X", 2022, 6.6), ("Smile", 2022, 6.5), ("Barbarian", 2022, 7.0),
        ("Nope", 2022, 6.8), ("The Black Phone", 2021, 7.0), ("Talk to Me", 2023, 7.1),
        ("M3GAN", 2022, 6.4), ("The Menu", 2022, 7.2), ("Bodies Bodies Bodies", 2022, 6.3),
        ("Malignant", 2021, 6.2), ("Old", 2021, 5.8), ("The Night House", 2020, 6.5),
        ("Host", 2020, 6.5), ("Relic", 2020, 6.3), ("His House", 2020, 6.5),
    ],
    "comedy": [
        ("The Hangover", 2009, 7.7), ("The Hangover Part II", 2011, 6.5), ("Superbad", 2007, 7.6),
        ("Step Brothers", 2008, 6.9), ("Bridesmaids", 2011, 6.8), ("21 Jump Street", 2012, 7.2),
        ("22 Jump Street", 2014, 7.0), ("The Grand Budapest Hotel", 2014, 8.1),
        ("Game Night", 2018, 6.9), ("Crazy Rich Asians", 2018, 6.9), ("Knives Out", 2019, 7.9),
        ("Glass Onion", 2022, 7.1), ("The Nice Guys", 2016, 7.4), ("Deadpool", 2016, 8.0),
        ("Deadpool 2", 2018, 7.7), ("Thor: Ragnarok", 2017, 7.9), ("Guardians of the Galaxy", 2014, 8.0),
        ("The Wolf of Wall Street", 2013, 8.2), ("Tropic Thunder", 2008, 7.0),
        ("Anchorman", 2004, 7.2), ("Anchorman 2", 2013, 6.3), ("Zoolander", 2001, 6.6),
        ("Napoleon Dynamite", 2004, 6.9), ("Elf", 2003, 7.1), ("Mean Girls", 2004, 7.1),
        ("Clueless", 1995, 6.9), ("Legally Blonde", 2001, 6.4), ("The Intern", 2015, 7.1),
        ("Pitch Perfect", 2012, 7.1), ("Pitch Perfect 2", 2015, 6.4), ("Easy A", 2010, 7.0),
        ("Juno", 2007, 7.4), ("Little Miss Sunshine", 2006, 7.8), ("Lady Bird", 2017, 7.4),
        ("Booksmart", 2019, 7.1), ("The Edge of Seventeen", 2016, 7.3), ("Palm Springs", 2020, 7.4),
        ("Free Guy", 2021, 7.1), ("Don't Look Up", 2021, 7.2), ("Glass Onion", 2022, 7.1),
        ("Bullet Train", 2022, 7.3), ("Amsterdam", 2022, 6.1), ("The Banshees of Inisherin", 2022, 7.7),
        ("Everything Everywhere All at Once", 2022, 7.8), ("Triangle of Sadness", 2022, 7.3),
        ("Barbie", 2023, 7.0), ("No Hard Feelings", 2023, 6.4),
    ],
    "action": [
        ("The Dark Knight", 2008, 9.0), ("The Dark Knight Rises", 2012, 8.4), ("Batman Begins", 2005, 8.2),
        ("Mad Max: Fury Road", 2015, 8.1), ("John Wick", 2014, 7.4), ("John Wick: Chapter 2", 2017, 7.5),
        ("John Wick: Chapter 3", 2019, 7.4), ("John Wick: Chapter 4", 2023, 7.7),
        ("Mission: Impossible - Fallout", 2018, 7.7), ("Mission: Impossible - Rogue Nation", 2015, 7.4),
        ("Mission: Impossible - Dead Reckoning", 2023, 7.7), ("Top Gun: Maverick", 2022, 8.3),
        ("Gladiator", 2000, 8.5), ("Die Hard", 1988, 8.2), ("Die Hard 2", 1990, 7.2),
        ("The Matrix", 1999, 8.7), ("The Matrix Reloaded", 2003, 7.2), ("The Matrix Resurrections", 2021, 5.7),
        ("Inception", 2010, 8.8), ("Tenet", 2020, 7.3), ("The Dark Knight", 2008, 9.0),
        ("Fast & Furious 7", 2015, 7.1), ("Fast & Furious 8", 2017, 6.6), ("Fast X", 2023, 5.8),
        ("Extraction", 2020, 6.7), ("Extraction 2", 2023, 7.0), ("The Gray Man", 2022, 6.5),
        ("The Old Guard", 2020, 6.6), ("Army of the Dead", 2021, 5.8), ("Red Notice", 2021, 6.3),
        ("6 Underground", 2019, 6.1), ("Kate", 2021, 6.2), ("Gunpowder Milkshake", 2021, 5.9),
        ("Nobody", 2021, 7.4), ("Wrath of Man", 2021, 7.1), ("The Tomorrow War", 2021, 6.5),
        ("Snake Eyes", 2021, 5.3), ("Black Widow", 2021, 6.7), ("Shang-Chi", 2021, 7.4),
        ("The Suicide Squad", 2021, 7.2), ("Bullet Train", 2022, 7.3), ("The Batman", 2022, 7.8),
        ("Avatar: The Way of Water", 2022, 7.6), ("Black Panther: Wakanda Forever", 2022, 6.7),
    ],
    "drama": [
        ("The Shawshank Redemption", 1994, 9.3), ("Forrest Gump", 1994, 8.8), ("The Godfather", 1972, 9.2),
        ("The Godfather Part II", 1974, 9.0), ("Schindler's List", 1993, 9.0), ("Parasite", 2019, 8.5),
        ("Whiplash", 2014, 8.5), ("The Social Network", 2010, 7.8), ("Bohemian Rhapsody", 2018, 7.9),
        ("A Beautiful Mind", 2001, 8.2), ("The Pursuit of Happyness", 2006, 8.0), ("Green Book", 2018, 8.2),
        ("1917", 2019, 8.2), ("Dunkirk", 2017, 7.8), ("Hacksaw Ridge", 2016, 8.1),
        ("The Revenant", 2015, 8.0), ("The Theory of Everything", 2014, 7.7), ("The Imitation Game", 2014, 8.0),
        ("12 Years a Slave", 2013, 8.1), ("Dallas Buyers Club", 2013, 8.0), ("The King's Speech", 2010, 8.0),
        ("Spotlight", 2015, 8.1), ("Manchester by the Sea", 2016, 7.8), ("Moonlight", 2016, 7.4),
        ("Three Billboards Outside Ebbing, Missouri", 2017, 8.1), ("Marriage Story", 2019, 7.9),
        ("Judy", 2019, 6.8), ("Joker", 2019, 8.4), ("Ford v Ferrari", 2019, 8.1),
        ("The Father", 2020, 8.2), ("Nomadland", 2020, 7.3), ("Promising Young Woman", 2020, 7.5),
        ("Sound of Metal", 2019, 7.8), ("Minari", 2020, 7.5), ("The Trial of the Chicago 7", 2020, 7.8),
        ("Mank", 2020, 6.8), ("The Power of the Dog", 2021, 6.9), ("CODA", 2021, 8.0),
        ("Belfast", 2021, 7.3), ("King Richard", 2021, 7.5), ("The Fabelmans", 2022, 7.5),
        ("Elvis", 2022, 7.3), ("Blonde", 2022, 5.4), ("Women Talking", 2022, 6.9),
        ("Tár", 2022, 7.3), ("The Whale", 2022, 7.7), ("Oppenheimer", 2023, 8.5),
    ],
    "sci-fi": [
        ("Interstellar", 2014, 8.6), ("Blade Runner 2049", 2017, 8.0), ("Dune", 2021, 8.0),
        ("Dune: Part Two", 2024, 8.5), ("Arrival", 2016, 7.9), ("Ex Machina", 2014, 7.7),
        ("The Martian", 2015, 8.0), ("Gravity", 2013, 7.7), ("Edge of Tomorrow", 2014, 7.9),
        ("Annihilation", 2018, 6.8), ("Blade Runner", 1982, 8.1), ("Alien", 1979, 8.5),
        ("Aliens", 1986, 8.4), ("Terminator 2: Judgment Day", 1991, 8.6), ("The Terminator", 1984, 8.1),
        ("Jurassic Park", 1993, 8.2), ("Jurassic World", 2015, 7.0), ("Jurassic World: Dominion", 2022, 5.6),
        ("E.T. the Extra-Terrestrial", 1982, 7.9), ("Close Encounters of the Third Kind", 1977, 7.6),
        ("War of the Worlds", 2005, 6.5), ("District 9", 2009, 7.9), ("Elysium", 2013, 6.6),
        ("Avatar", 2009, 7.9), ("Avatar: The Way of Water", 2022, 7.6), ("Star Wars: Episode IV", 1977, 8.6),
        ("Star Wars: Episode V", 1980, 8.7), ("Star Wars: Episode VI", 1983, 8.3),
        ("Star Wars: The Force Awakens", 2015, 7.8), ("Rogue One", 2016, 7.8),
        ("Prometheus", 2012, 7.0), ("Alien: Covenant", 2017, 6.4), ("The Cloverfield Paradox", 2018, 5.5),
        ("Midnight Special", 2016, 6.6), ("Upgrade", 2018, 7.5), ("Alita: Battle Angel", 2019, 7.3),
        ("Ad Astra", 2019, 6.5), ("Tenet", 2020, 7.3), ("The Midnight Sky", 2020, 5.6),
        ("Stowaway", 2021, 5.7), ("The Adam Project", 2022, 6.7), ("Everything Everywhere All at Once", 2022, 7.8),
        ("Nope", 2022, 6.8), ("M3GAN", 2022, 6.4), ("65", 2023, 5.4),
    ],
    "romance": [
        ("The Notebook", 2004, 7.8), ("La La Land", 2016, 8.0), ("Titanic", 1997, 7.9),
        ("Pride & Prejudice", 2005, 7.8), ("500 Days of Summer", 2009, 7.7), ("Before Sunrise", 1995, 8.1),
        ("Before Sunset", 2004, 8.1), ("Before Midnight", 2013, 8.0), ("Eternal Sunshine of the Spotless Mind", 2004, 8.3),
        ("The Proposal", 2009, 6.7), ("Crazy, Stupid, Love", 2011, 7.4), ("Silver Linings Playbook", 2012, 7.7),
        ("About Time", 2013, 7.8), ("The Fault in Our Stars", 2014, 7.7), ("Me Before You", 2016, 7.4),
        ("To All the Boys I've Loved Before", 2018, 7.1), ("Crazy Rich Asians", 2018, 6.9),
        ("A Star Is Born", 2018, 7.6), ("Five Feet Apart", 2019, 7.2), ("After", 2019, 5.3),
        ("The Sun Is Also a Star", 2019, 5.8), ("All the Bright Places", 2020, 6.5),
        ("The Kissing Booth", 2018, 5.9), ("The Kissing Booth 2", 2020, 5.8), ("The Kissing Booth 3", 2021, 5.6),
        ("Purple Hearts", 2022, 6.0), ("The Hating Game", 2021, 6.1), ("Love Hard", 2021, 6.3),
        ("Love in the Villa", 2022, 5.4), ("A Perfect Pairing", 2022, 5.8), ("Persuasion", 2022, 5.4),
        ("Look Both Ways", 2022, 6.0), ("Hello, Goodbye, and Everything in Between", 2022, 5.7),
        ("Anyone But You", 2023, 6.1), ("One True Loves", 2023, 5.6),
    ],
    "thriller": [
        ("Gone Girl", 2014, 8.1), ("Shutter Island", 2010, 8.2), ("The Prestige", 2006, 8.5),
        ("Se7en", 1995, 8.6), ("Prisoners", 2013, 8.1), ("Zodiac", 2007, 7.7),
        ("Nightcrawler", 2014, 7.8), ("Sicario", 2015, 7.6), ("Sicario: Day of the Soldado", 2018, 7.1),
        ("Wind River", 2017, 7.7), ("Hell or High Water", 2016, 7.6), ("The Girl with the Dragon Tattoo", 2011, 7.8),
        ("The Girl on the Train", 2016, 6.5), ("A Simple Favor", 2018, 6.8), ("The Invisible Man", 2020, 7.1),
        ("Run", 2020, 6.8), ("I Care a Lot", 2020, 6.3), ("Malcolm & Marie", 2021, 5.7),
        ("The Woman in the Window", 2021, 5.7), ("Kate", 2021, 6.2), ("Fear Street Part 1: 1994", 2021, 6.2),
        ("Fear Street Part 2: 1978", 2021, 6.7), ("Fear Street Part 3: 1666", 2021, 6.6),
        ("No Exit", 2022, 6.1), ("Kimi", 2022, 6.3), ("The Weekend Away", 2022, 5.4),
        ("Spiderhead", 2022, 5.4), ("Hustle", 2022, 7.3), ("Ambulance", 2022, 6.1),
        ("Memory", 2022, 6.1), ("Deep Water", 2022, 5.4), ("The Good Nurse", 2022, 6.6),
        ("Glass Onion", 2022, 7.1), ("See How They Run", 2022, 6.5), ("Don't Worry Darling", 2022, 6.2),
        ("Missing", 2023, 7.0), ("The Covenant", 2023, 7.6),
    ],
    "animation": [
        ("Spirited Away", 2001, 8.6), ("Your Name", 2016, 8.4), ("Coco", 2017, 8.4),
        ("Soul", 2020, 8.0), ("Inside Out", 2015, 8.2), ("Inside Out 2", 2024, 7.6),
        ("Up", 2009, 8.3), ("WALL-E", 2008, 8.4), ("Finding Nemo", 2003, 8.2),
        ("Finding Dory", 2016, 7.3), ("Toy Story", 1995, 8.3), ("Toy Story 2", 1999, 7.9),
        ("Toy Story 3", 2010, 8.3), ("Toy Story 4", 2019, 7.7), ("The Incredibles", 2004, 8.0),
        ("Incredibles 2", 2018, 7.6), ("Monsters, Inc.", 2001, 8.1), ("Ratatouille", 2007, 8.1),
        ("How to Train Your Dragon", 2010, 8.1), ("How to Train Your Dragon 2", 2014, 7.8),
        ("Shrek", 2001, 7.9), ("Shrek 2", 2004, 7.4), ("Frozen", 2013, 7.4),
        ("Frozen II", 2019, 6.8), ("Moana", 2016, 7.6), ("Encanto", 2021, 7.2),
        ("Turning Red", 2022, 7.0), ("Lightyear", 2022, 5.8), ("Puss in Boots: The Last Wish", 2022, 7.9),
        ("Spider-Man: Into the Spider-Verse", 2018, 8.4), ("Spider-Man: Across the Spider-Verse", 2023, 8.6),
        ("Elemental", 2023, 7.0), ("Wish", 2023, 5.6), ("The Super Mario Bros. Movie", 2023, 7.0),
        ("Suzume", 2022, 7.6), ("The Boy and the Heron", 2023, 7.5),
        ("Luca", 2021, 7.4), ("Raya and the Last Dragon", 2021, 7.3),
    ],
    "documentary": [
        ("The Social Dilemma", 2020, 7.6), ("Our Planet", 2019, 9.3), ("My Octopus Teacher", 2020, 8.1),
        ("13th", 2016, 8.2), ("Making a Murderer", 2015, 8.5), ("The Last Dance", 2020, 9.0),
        ("Free Solo", 2018, 8.1), ("Won't You Be My Neighbor?", 2018, 8.4), ("RBG", 2018, 7.6),
        ("Tiger King", 2020, 7.5), ("The Tinder Swindler", 2022, 7.0), ("Downfall: The Case Against Boeing", 2022, 7.5),
        ("The Puppet Master", 2022, 6.8), ("Bad Vegan", 2022, 6.4), ("Keep Sweet: Pray and Obey", 2022, 7.1),
        ("The Staircase", 2022, 7.1), ("Inventing Anna", 2022, 6.7), ("Jimmy Savile: A British Horror Story", 2022, 7.0),
        ("The Most Hated Man on the Internet", 2022, 7.2), ("Stutz", 2022, 7.6),
    ],
    "superhero": [
        ("The Dark Knight", 2008, 9.0), ("Avengers: Endgame", 2019, 8.4), ("Avengers: Infinity War", 2018, 8.4),
        ("Spider-Man: No Way Home", 2021, 8.2), ("Black Panther", 2018, 7.3), ("Guardians of the Galaxy", 2014, 8.0),
        ("Guardians of the Galaxy Vol. 2", 2017, 7.6), ("Guardians of the Galaxy Vol. 3", 2023, 7.9),
        ("Iron Man", 2008, 7.9), ("Thor", 2011, 7.0), ("Thor: Ragnarok", 2017, 7.9),
        ("Captain America: Civil War", 2016, 7.8), ("Doctor Strange", 2016, 7.5),
        ("Doctor Strange in the Multiverse of Madness", 2022, 6.9), ("Shang-Chi", 2021, 7.4),
        ("Eternals", 2021, 6.3), ("Black Widow", 2021, 6.7), ("The Batman", 2022, 7.8),
        ("Black Adam", 2022, 6.3), ("Aquaman", 2018, 6.9), ("Wonder Woman", 2017, 7.4),
        ("Wonder Woman 1984", 2020, 5.4), ("The Flash", 2023, 6.5), ("Blue Beetle", 2023, 6.0),
        ("Ant-Man and the Wasp: Quantumania", 2023, 6.0), ("The Marvels", 2023, 5.5),
    ],
    "mystery": [
        ("Knives Out", 2019, 7.9), ("Glass Onion", 2022, 7.1), ("Gone Girl", 2014, 8.1),
        ("Shutter Island", 2010, 8.2), ("The Prestige", 2006, 8.5), ("Prisoners", 2013, 8.1),
        ("Zodiac", 2007, 7.7), ("Murder on the Orient Express", 2017, 6.5),
        ("Death on the Nile", 2022, 6.3), ("The Woman in the Window", 2021, 5.7),
        ("Enola Holmes", 2020, 6.6), ("Enola Holmes 2", 2022, 6.8), ("See How They Run", 2022, 6.5),
        ("Amsterdam", 2022, 6.1), ("A Haunting in Venice", 2023, 6.6),
    ],
    "crime": [
        ("The Godfather", 1972, 9.2), ("The Godfather Part II", 1974, 9.0), ("Goodfellas", 1990, 8.7),
        ("The Departed", 2006, 8.5), ("Pulp Fiction", 1994, 8.9), ("City of God", 2002, 8.6),
        ("Heat", 1995, 8.3), ("The Usual Suspects", 1995, 8.5), ("Casino", 1995, 8.2),
        ("Scarface", 1983, 8.3), ("The Town", 2010, 7.5), ("Drive", 2011, 7.8),
        ("Baby Driver", 2017, 7.6), ("Den of Thieves", 2018, 7.0), ("Widows", 2018, 6.9),
        ("The Irishman", 2019, 7.8), ("Uncut Gems", 2019, 7.4), ("The Gentlemen", 2019, 7.8),
        ("Wrath of Man", 2021, 7.1), ("The Guilty", 2021, 6.3), ("Army of Thieves", 2021, 6.4),
        ("Hustle", 2022, 7.3), ("Glass Onion", 2022, 7.1), ("Amsterdam", 2022, 6.1),
    ],
    "family": [
        ("Coco", 2017, 8.4), ("Encanto", 2021, 7.2), ("Luca", 2021, 7.4), ("Soul", 2020, 8.0),
        ("Moana", 2016, 7.6), ("Frozen", 2013, 7.4), ("Frozen II", 2019, 6.8),
        ("The Lion King", 1994, 8.5), ("Aladdin", 1992, 8.0), ("The Little Mermaid", 1989, 7.6),
        ("Beauty and the Beast", 1991, 8.0), ("Shrek", 2001, 7.9), ("Shrek 2", 2004, 7.4),
        ("How to Train Your Dragon", 2010, 8.1), ("Paddington", 2014, 7.2), ("Paddington 2", 2017, 7.8),
        ("The Mitchells vs. the Machines", 2021, 7.6), ("The Bad Guys", 2022, 6.8),
        ("Puss in Boots: The Last Wish", 2022, 7.9), ("The Super Mario Bros. Movie", 2023, 7.0),
        ("Elemental", 2023, 7.0), ("Wish", 2023, 5.6), ("Wonka", 2023, 7.1),
    ],
    "adventure": [
        ("Raiders of the Lost Ark", 1981, 8.4), ("Indiana Jones and the Last Crusade", 1989, 8.2),
        ("Pirates of the Caribbean: The Curse of the Black Pearl", 2003, 8.0),
        ("The Lord of the Rings: The Fellowship of the Ring", 2001, 8.8),
        ("The Lord of the Rings: The Two Towers", 2002, 8.8),
        ("The Lord of the Rings: The Return of the King", 2003, 9.0),
        ("The Hobbit: An Unexpected Journey", 2012, 7.8), ("Jurassic Park", 1993, 8.2),
        ("Jurassic World", 2015, 7.0), ("The Jungle Book", 2016, 7.4), ("Life of Pi", 2012, 7.9),
        ("Cast Away", 2000, 7.8), ("The Revenant", 2015, 8.0), ("Into the Wild", 2007, 8.1),
        ("1917", 2019, 8.2), ("Uncharted", 2022, 6.3), ("The Lost City", 2022, 6.1),
        ("Jungle Cruise", 2021, 6.6), ("Black Panther", 2018, 7.3), ("Avatar", 2009, 7.9),
        ("Avatar: The Way of Water", 2022, 7.6), ("Dune", 2021, 8.0), ("Dune: Part Two", 2024, 8.5),
    ],
}

def generate_database():
    movies = []
    seen = set()
    
    for primary_genre, movie_list in MOVIES_BY_GENRE.items():
        for title, year, rating in movie_list:
            if title in seen:
                continue
            seen.add(title)
            
            # Determine genres based on which lists this movie appears in
            genres = [primary_genre]
            for genre, genre_movies in MOVIES_BY_GENRE.items():
                if genre != primary_genre:
                    for t, _, _ in genre_movies:
                        if t == title:
                            genres.append(genre)
                            break
            
            movies.append({
                'title': title,
                'year': year,
                'rating': rating,
                'genres': genres[:3],
                'description': f"A {year} {genres[0]} film rated {rating}/10."
            })
    
    # Sort by rating
    movies.sort(key=lambda x: x['rating'], reverse=True)
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({'movies': movies}, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(movies)} movies to {output_path}")
    
    # Show stats
    genre_counts = {}
    for m in movies:
        for g in m['genres']:
            genre_counts[g] = genre_counts.get(g, 0) + 1
    
    print("\nGenre distribution:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        print(f"  {genre}: {count}")

if __name__ == '__main__':
    generate_database()
