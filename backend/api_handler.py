import requests
from backend.config import API_KEY, BASE_URL 



class APIHandler:
    @classmethod
    def fetch_movie_details(cls, movie_id):
        if not movie_id:
            print("Error: No movie ID provided.")
            return None

        endpoint = f"{BASE_URL}/movie/{movie_id}"
        params = {
            "api_key": API_KEY,
            "language": "en-US",
        }

        try:
            print(f"Requesting movie details for movie_id: {movie_id}")
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error: Unable to fetch movie details for movie_id {movie_id}. Status code {response.status_code}")
                print(f"Response content: {response.text}")
        except Exception as e:
            print(f"Exception occurred while fetching movie details: {e}")

        return None

    @classmethod
    def fetch_movies_by_query(cls, query, content_type="movie"):
        """
        Search for movies or TV series based on a query.
        :param query: The search keyword or phrase.
        :param content_type: Type of content to search for ('movie' or 'tv').
        :return: List of movies/TV series matching the query or an empty list if an error occurs.
        """
        endpoint = f"{BASE_URL}/search/{content_type}"
        params = {
            "api_key": API_KEY,
            "query": query,
            "language": "en-US",
            "page": 1,
        }

        try:
            print(f"Searching for {content_type} with query: {query}")
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                # Debugging: print results to check movie IDs
                if not results:
                    print(f"No results found for query: {query}")
                else:
                    print(f"Found {len(results)} results:")
                    for movie in results:
                        title = movie.get("title") if content_type == "movie" else movie.get("name")
                        print(f"Movie ID: {movie.get('id')}, Title: {title}")

                # Filter out results without valid IDs
                valid_results = [movie for movie in results if movie.get("id")]
                return valid_results
            else:
                print(f"Error: Unable to fetch search results. Status code {response.status_code}")
                print(f"Response content: {response.text}")
        except Exception as e:
            print(f"Error fetching search results: {e}")

        return []

