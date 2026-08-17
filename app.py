from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import os
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

app = Flask(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/multi"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"
TMDB_TV_URL = "https://api.themoviedb.org/3/tv"

TMDB_TRENDING_URL = "https://api.themoviedb.org/3/trending/all/week"


# =========================================================
# BASIC HELPERS
# =========================================================

def normalize_text(text):
    return "".join(
        char.lower()
        for char in text
        if char.isalnum()
    )


def similarity_score(query, title):
    query = normalize_text(query)
    title = normalize_text(title)

    if not query or not title:
        return 0

    return SequenceMatcher(
        None,
        query,
        title
    ).ratio()


def get_item_title(item):
    if item.get("media_type") == "movie":
        return item.get("title", "")

    return item.get("name", "")


# =========================================================
# SEARCH
# =========================================================

def tmdb_search(query):

    try:

        response = requests.get(
            TMDB_SEARCH_URL,
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "include_adult": False
            },
            timeout=8
        )

        if response.status_code != 200:
            return []

        data = response.json()

        results = []

        for item in data.get("results", []):

            if item.get("media_type") in ["movie", "tv"]:
                results.append(item)

        return results

    except requests.RequestException:
        return []


# =========================================================
# TITLE DETAILS
# =========================================================

def get_title_details(media_type, media_id):

    if media_type == "movie":
        url = f"{TMDB_MOVIE_URL}/{media_id}"

    elif media_type == "tv":
        url = f"{TMDB_TV_URL}/{media_id}"

    else:
        return None

    try:

        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY
            },
            timeout=8
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None


# =========================================================
# LANGUAGES
# =========================================================

def get_languages(item):

    details = get_title_details(
        item.get("media_type"),
        item.get("id")
    )

    languages = []

    if details:

        for language in details.get(
            "spoken_languages",
            []
        ):

            name = language.get("english_name")

            if name:
                languages.append(name)

    item["languages"] = languages

    return item


def add_languages_to_results(results):

    results_to_process = results[:6]
    remaining_results = results[6:]

    processed_results = []

    with ThreadPoolExecutor(max_workers=6) as executor:

        futures = [
            executor.submit(
                get_languages,
                item
            )
            for item in results_to_process
        ]

        for future in as_completed(futures):

            try:
                processed_results.append(
                    future.result()
                )

            except Exception:
                pass

    processed_map = {
        (
            item.get("media_type"),
            item.get("id")
        ): item
        for item in processed_results
    }

    final_results = []

    for item in results_to_process:

        key = (
            item.get("media_type"),
            item.get("id")
        )

        if key in processed_map:
            final_results.append(
                processed_map[key]
            )
        else:
            item["languages"] = []
            final_results.append(item)

    for item in remaining_results:
        item["languages"] = []
        final_results.append(item)

    return final_results


# =========================================================
# TOP 10 FOR HOMEPAGE
# =========================================================

def get_top_10_picks():

    try:

        response = requests.get(
            TMDB_TRENDING_URL,
            params={
                "api_key": TMDB_API_KEY
            },
            timeout=8
        )

        if response.status_code != 200:
            return []

        data = response.json()

        picks = []

        for item in data.get("results", []):

            if item.get("media_type") in ["movie", "tv"]:

                picks.append(item)

            if len(picks) == 10:
                break

        return picks

    except requests.RequestException:
        return []


# =========================================================
# SIMILAR TITLES
# =========================================================

def get_similar_titles(media_type, media_id, current_title):

    if media_type == "movie":
        url = f"{TMDB_MOVIE_URL}/{media_id}/similar"

    elif media_type == "tv":
        url = f"{TMDB_TV_URL}/{media_id}/similar"

    else:
        return []

    try:

        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US",
                "page": 1
            },
            timeout=8
        )

        if response.status_code != 200:
            return []

        data = response.json()

        similar = []

        for item in data.get("results", []):

            item["media_type"] = media_type

            title = (
                item.get("title")
                or item.get("name")
                or ""
            )

            if not title:
                continue

            # Don't show the exact searched title again
            if normalize_text(title) == normalize_text(current_title):
                continue

            similar.append(item)

            if len(similar) == 5:
                break

        return similar

    except requests.RequestException:
        return []


# =========================================================
# TYPO / FUZZY SEARCH
# =========================================================

def get_fuzzy_candidates():

    candidates = []

    # Trending
    urls = [
        (
            "https://api.themoviedb.org/3/trending/all/week",
            "unknown",
            1
        )
    ]

    # Popular movies - first 5 pages
    for page in range(1, 6):

        urls.append(
            (
                "https://api.themoviedb.org/3/movie/popular",
                "movie",
                page
            )
        )

    # Popular TV - first 5 pages
    for page in range(1, 6):

        urls.append(
            (
                "https://api.themoviedb.org/3/tv/popular",
                "tv",
                page
            )
        )

    def fetch_candidates(task):

        url, media_type, page = task

        try:

            response = requests.get(
                url,
                params={
                    "api_key": TMDB_API_KEY,
                    "page": page
                },
                timeout=8
            )

            if response.status_code != 200:
                return []

            data = response.json()

            page_results = []

            for item in data.get("results", []):

                if media_type == "unknown":

                    if item.get("media_type") not in [
                        "movie",
                        "tv"
                    ]:
                        continue

                else:

                    item["media_type"] = media_type

                page_results.append(item)

            return page_results

        except requests.RequestException:

            return []

    # Run requests simultaneously
    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = [
            executor.submit(
                fetch_candidates,
                task
            )
            for task in urls
        ]

        for future in as_completed(futures):

            try:

                candidates.extend(
                    future.result()
                )

            except Exception:

                pass

    # Remove duplicates
    unique_candidates = {}

    for item in candidates:

        key = (
            item.get("media_type"),
            item.get("id")
        )

        unique_candidates[key] = item

    return list(
        unique_candidates.values()
    )


def find_correction(query):

    candidates = get_fuzzy_candidates()

    query_normalized = normalize_text(query)

    best_match = None
    best_score = 0

    for item in candidates:

        title = (
            item.get("title")
            or
            item.get("name")
            or
            ""
        )

        if not title:
            continue

        title_normalized = normalize_text(title)

        # Exact match
        if query_normalized == title_normalized:
            continue

        score = SequenceMatcher(
            None,
            query_normalized,
            title_normalized
        ).ratio()

        if score > best_score:

            best_score = score
            best_match = item

    # Only show suggestion when similarity is strong
    if best_match and best_score >= 0.70:

        title = (
            best_match.get("title")
            or
            best_match.get("name")
            or
            ""
        )

        return {
            "title": title,
            "media_type": best_match.get(
                "media_type"
            ),
            "id": best_match.get("id"),
            "score": best_score
        }

    return None


def find_correction(query):

    candidates = get_fuzzy_candidates()

    best_match = None
    best_score = 0

    for item in candidates:

        title = (
            item.get("title")
            or item.get("name")
            or ""
        )

        if not title:
            continue

        score = similarity_score(
            query,
            title
        )

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= 0.68:

        title = (
            best_match.get("title")
            or best_match.get("name")
            or ""
        )

        if normalize_text(query) != normalize_text(title):

            return {
                "title": title,
                "media_type": best_match.get("media_type"),
                "id": best_match.get("id")
            }

    return None


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    top_picks = get_top_10_picks()

    return render_template(
        "index.html",
        results=[],
        query="",
        suggestion=None,
        top_picks=top_picks,
        similar_titles=[]
    )


# =========================================================
# SEARCH
# =========================================================

@app.route("/search")
def search():

    query = request.args.get(
        "query",
        ""
    ).strip()

    if not query:

        return home()

    results = tmdb_search(query)

    suggestion = None
    similar_titles = []

    # -----------------------------------------------------
    # SEARCH RESULTS
    # -----------------------------------------------------

    if results:

        # Sort results according to similarity
        results.sort(
            key=lambda item:
                similarity_score(
                    query,
                    get_item_title(item)
                ),
            reverse=True
        )

        results = results[:12]

        # Get languages
        results = add_languages_to_results(
            results
        )

        # -------------------------------------------------
        # SIMILAR TITLES
        # -------------------------------------------------

        first_result = results[0]

        first_title = get_item_title(
            first_result
        )

        similar_titles = get_similar_titles(
            first_result.get("media_type"),
            first_result.get("id"),
            first_title
        )

    else:

        # No exact search result
        # Try to find a close match

        suggestion = find_correction(query)

    return render_template(
        "index.html",
        results=results,
        query=query,
        suggestion=suggestion,
        top_picks=[],
        similar_titles=similar_titles
    )


# =========================================================
# DETAILS / OTT AVAILABILITY
# =========================================================

@app.route(
    "/details/<media_type>/<int:media_id>"
)
def details(media_type, media_id):

    if media_type == "movie":

        details_url = (
            f"{TMDB_MOVIE_URL}/{media_id}"
        )

        providers_url = (
            f"{TMDB_MOVIE_URL}/{media_id}"
            "/watch/providers"
        )

    elif media_type == "tv":

        details_url = (
            f"{TMDB_TV_URL}/{media_id}"
        )

        providers_url = (
            f"{TMDB_TV_URL}/{media_id}"
            "/watch/providers"
        )

    else:

        return "Invalid media type", 400

    params = {
        "api_key": TMDB_API_KEY
    }

    # -----------------------------------------------------
    # TITLE DETAILS
    # -----------------------------------------------------

    try:

        details_response = requests.get(
            details_url,
            params=params,
            timeout=8
        )

    except requests.RequestException:

        return (
            "Unable to get title information",
            500
        )

    if details_response.status_code != 200:

        return (
            "Unable to get title information",
            500
        )

    title_data = details_response.json()

    # -----------------------------------------------------
    # OTT PROVIDERS
    # -----------------------------------------------------

    try:

        providers_response = requests.get(
            providers_url,
            params=params,
            timeout=8
        )

    except requests.RequestException:

        return (
            "Unable to get OTT information",
            500
        )

    if providers_response.status_code != 200:

        return (
            "Unable to get OTT information",
            500
        )

    provider_data = providers_response.json()

    india_data = provider_data.get(
        "results",
        {}
    ).get(
        "IN",
        {}
    )

    return render_template(
        "details.html",
        title_data=title_data,
        provider_data=india_data,
        media_type=media_type,
        media_id=media_id
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

