import requests
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import random
from backend.config import BASE_URL, API_KEY

class CineGuruBackend:
    def __init__(self):
        self.emotion_detector = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.session = requests.Session()
        self.session.params = {
            "api_key": API_KEY,
            "language": "en-US"
        }

        # Revised emotion-to-genre mapping with more appropriate emotional matches
        self.emotion_genre_mapping = {
            "joy": [
                ("35", 0.8),  # Comedy
                ("10751", 0.7),  # Family
                ("16", 0.6)  # Animation
            ],
            "sadness": [
                ("18", 0.9),  # Drama - primary match for sadness
                ("10749", 0.7),  # Romance - can be cathartic
                ("18,10751", 0.6),  # Drama + Family - uplifting but not jarring
            ],
            "anger": [
                ("18", 0.8),  # Drama
                ("28", 0.6),  # Action
                ("53", 0.5)  # Thriller
            ],
            "fear": [
                ("18", 0.8),  # Drama
                ("9648", 0.7),  # Mystery
                ("53", 0.6)  # Thriller
            ],
            "surprise": [
                ("878", 0.7),  # Science Fiction
                ("12", 0.6),  # Adventure
                ("14", 0.5)  # Fantasy
            ],
            "neutral": [
                ("18", 0.7),  # Drama
                ("99", 0.6),  # Documentary
                ("36", 0.5)  # History
            ]
        }

        # Add emotional transition mapping for gradual mood shifts
        self.emotional_transitions = {
            "sadness": {
                "primary": ["18"],  # Drama first
                "secondary": ["18,10751"],  # Drama + Family
                "tertiary": ["10749"]  # Romance
            }
        }


    def detect_emotions(self, user_input, top_n=3):
        try:
            results = self.emotion_detector(user_input)
            emotion_scores = {res['label'].lower(): res['score'] for res in results[0]}
            
            MIN_CONFIDENCE = 0.1
            valid_emotions = {k: v for k, v in emotion_scores.items() if v > MIN_CONFIDENCE}
            
            sorted_emotions = sorted(valid_emotions.items(), key=lambda x: x[1], reverse=True)
            top_emotions = dict(sorted_emotions[:top_n])
            
            print(f"Detected emotions: {top_emotions}")
            return top_emotions if top_emotions else None
            
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return None

    def fetch_movies_for_emotion(self, emotion, emotion_score):
        """
        Fetch movies specifically tailored for an emotion with appropriate transitions
        """
        movies = []
        
        if emotion == "sadness":
            # For sadness, follow a specific emotional arc
            transitions = self.emotional_transitions["sadness"]
            
            # Start with pure dramas that acknowledge the emotion
            primary_movies = self.fetch_movies(transitions["primary"][0], max_pages=10, movies_per_genre=5)
            movies.extend([(movie, 0.9) for movie in primary_movies])
            
            # Add some uplifting dramas
            secondary_movies = self.fetch_movies(transitions["secondary"][0], max_pages=10, movies_per_genre=3)
            movies.extend([(movie, 0.7) for movie in secondary_movies])
            
            # Add a few romantic movies for emotional catharsis
            tertiary_movies = self.fetch_movies(transitions["tertiary"][0], max_pages=10, movies_per_genre=2)
            movies.extend([(movie, 0.5) for movie in tertiary_movies])
        else:
            # Handle other emotions with standard genre mapping
            for genre_id, weight in self.emotion_genre_mapping.get(emotion, []):
                genre_movies = self.fetch_movies(genre_id, max_pages=10, movies_per_genre=5)
                movies.extend([(movie, weight) for movie in genre_movies])
        
        return movies

    def fetch_movies(self, genre_id, max_pages=10, movies_per_genre=5):
        """
        Enhanced movie fetching with improved randomization
        """
        try:
            all_results = []
            fetched_ids = set()
            
            initial_response = self.session.get(f"{BASE_URL}/discover/movie", params={
                "with_genres": genre_id,
                "page": 1
            })
            total_pages = min(initial_response.json().get("total_pages", 1), 500)
            
            pages_to_fetch = random.sample(
                range(1, total_pages + 1),
                min(max_pages, total_pages)
            )
            
            for page in pages_to_fetch:
                response = self.session.get(f"{BASE_URL}/discover/movie", params={
                    "with_genres": genre_id,
                    "sort_by": "vote_average.desc",
                    "vote_count.gte": 100,
                    "page": page,
                    "with_original_language": "en"
                })
                
                if response.status_code == 200:
                    movies = response.json().get("results", [])
                    random.shuffle(movies)
                    
                    for movie in movies:
                        if (movie.get("id") not in fetched_ids and 
                            movie.get("vote_average", 0) >= 6.5 and  # Higher quality threshold
                            movie.get("overview")):
                            all_results.append(movie)
                            fetched_ids.add(movie.get("id"))
            
            random.shuffle(all_results)
            return all_results[:movies_per_genre]
            
        except requests.RequestException as e:
            print(f"Error fetching movies: {e}")
            return []

    def recommend_movies(self, user_input):
        """
        Enhanced recommendation system with emotional awareness
        """
        detected_emotions = self.detect_emotions(user_input)
        if not detected_emotions:
            return "Could not detect emotions from input. Please try again with more detailed feelings."

        all_movies = []
        for emotion, score in detected_emotions.items():
            emotion_movies = self.fetch_movies_for_emotion(emotion, score)
            all_movies.extend([(movie, weight * score) for movie, weight in emotion_movies])

        if not all_movies:
            return "No suitable movies found. Please try again with different emotions."

        query_embedding = self.similarity_model.encode(user_input)
        recommendations = []
        
        for movie, emotion_weight in all_movies:
            if movie.get("overview"):
                plot_embedding = self.similarity_model.encode(movie["overview"])
                similarity_score = util.cos_sim(query_embedding, plot_embedding).item()
                
                final_score = (similarity_score + emotion_weight) / 2
                
                recommendations.append((
                    final_score,
                    {
                        "title": movie.get("title", "Unknown"),
                        "overview": movie.get("overview", ""),
                        "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
                        "movie_id": movie.get("id"),
                        "vote_average": movie.get("vote_average", 0),
                        "release_date": movie.get("release_date", "Unknown"),
                        "genre_ids": movie.get("genre_ids", [])
                    }
                ))

        recommendations.sort(reverse=True, key=lambda x: x[0])
        return recommendations[:5]

if __name__ == "__main__":
    cine_guru = CineGuruBackend()
    user_input = input("Describe how you're feeling and what kind of movie you'd like to watch: ")
    recommendations = cine_guru.recommend_movies(user_input)

    if isinstance(recommendations, str):
        print(recommendations)
    else:
        print("\nMovie Recommendations Based on Your Emotional State:")
        for score, movie in recommendations:
            print(f"Title: {movie['title']}")
            print(f"Release Date: {movie['release_date']}")
            print(f"Rating: {movie['vote_average']}/10")
            print(f"Overview: {movie['overview']}")
            print(f"Relevance Score: {score:.2f}")
            print("-" * 60)

