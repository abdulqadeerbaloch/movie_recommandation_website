
import os
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. LOAD NETFLIX DATASET
# ==========================================

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(
    BASE_FOLDER,
    "data",
    "netflix_titles.csv"
)

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(
        f"Netflix dataset not found: {CSV_FILE}"
    )

movies = pd.read_csv(CSV_FILE)

required_columns = [
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description"
]

missing_columns = [
    column for column in required_columns
    if column not in movies.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing columns: {missing_columns}"
    )


# ==========================================
# 2. CLEAN DATASET
# ==========================================

movies = movies.copy()

# Correct rows where duration was mistakenly stored in rating
wrong_rows = movies["rating"].astype(str).str.contains(
    "min",
    case=False,
    na=False
)

movies.loc[wrong_rows, "duration"] = movies.loc[
    wrong_rows, "rating"
]

movies.loc[wrong_rows, "rating"] = ""

text_columns = [
    "director",
    "cast",
    "country",
    "rating",
    "duration",
    "description",
    "listed_in"
]

for column in text_columns:
    movies[column] = movies[column].fillna("").astype(str)

movies["release_year"] = pd.to_numeric(
    movies["release_year"],
    errors="coerce"
)

movies = movies.dropna(
    subset=["title", "release_year"]
)

movies["release_year"] = movies["release_year"].astype(int)


# ==========================================
# 3. EXTRACT DURATION NUMBERS
# ==========================================

movies["number"] = pd.to_numeric(
    movies["duration"].str.split(" ").str[0],
    errors="coerce"
)


# ==========================================
# 4. CREATE CONTENT FEATURES
# ==========================================

movies["soup"] = (
    (movies["listed_in"] + " ") * 3
    + movies["description"] + " "
    + movies["cast"] + " "
    + movies["director"] + " "
    + movies["country"]
)

vectorizer = TfidfVectorizer(
    stop_words="english"
)

tfidf_matrix = vectorizer.fit_transform(
    movies["soup"]
)


# ==========================================
# 5. GENRE MAPPING
# ==========================================

GENRE_WORDS = {
    "Action": "action adventure",
    "Comedy": "comedies",
    "Drama": "dramas",
    "Romance": "romantic",
    "Thriller": "thrillers",
    "Horror": "horror",
    "Sci-Fi": "sci fi fantasy",
    "Fantasy": "fantasy sci fi",
    "Documentary": "documentaries docuseries"
}


# ==========================================
# 6. FILM INDUSTRY MAPPING
# ==========================================

INDUSTRY_COUNTRY = {
    "Hollywood": "United States",
    "Bollywood": "India",
    "Korean": "South Korea",
    "Japanese": "Japan"
}


# ==========================================
# 7. AUDIENCE RATINGS
# ==========================================

KIDS_RATINGS = [
    "G",
    "PG",
    "TV-Y",
    "TV-Y7",
    "TV-Y7-FV",
    "TV-G",
    "TV-PG"
]

ADULT_RATINGS = [
    "R",
    "NC-17",
    "TV-MA",
    "NR",
    "UR"
]


# ==========================================
# 8. RELEASE YEAR RANGES
# ==========================================

YEAR_RANGES = {
    "2020–2026": (2020, 2026),
    "2010–2019": (2010, 2019),
    "2000–2009": (2000, 2009),
    "Before 2000": (0, 1999)
}


# ==========================================
# 9. FILTER MOVIES
# ==========================================

def filter_movies(prefs):

    keep = pd.Series(
        True,
        index=movies.index
    )

    # CONTENT TYPE

    content_type = prefs.get("type", "Both")

    if content_type == "Movies":
        keep &= movies["type"] == "Movie"

    elif content_type == "TV Shows":
        keep &= movies["type"] == "TV Show"

    # FILM INDUSTRY

    industry = prefs.get("industry", "Any")

    if industry in INDUSTRY_COUNTRY:

        country = INDUSTRY_COUNTRY[industry]

        keep &= movies["country"].str.contains(
            country,
            case=False,
            regex=False
        )

    elif industry == "Other / International":

        in_selected_industries = pd.Series(
            False,
            index=movies.index
        )

        for country in INDUSTRY_COUNTRY.values():

            in_selected_industries |= movies["country"].str.contains(
                country,
                case=False,
                regex=False
            )

        keep &= (
            ~in_selected_industries
            & (movies["country"] != "")
        )

    # RELEASE YEAR

    year = prefs.get("year", "Any")

    if year in YEAR_RANGES:

        first_year, last_year = YEAR_RANGES[year]

        keep &= movies["release_year"].between(
            first_year,
            last_year
        )

    # AUDIENCE

    audience = prefs.get("audience", "Under 18")

    if audience == "Under 18":

        keep &= movies["rating"].isin(
            KIDS_RATINGS
        )

    elif audience == "Adult (18+)":

        keep &= movies["rating"].isin(
            ADULT_RATINGS
        )

    # DURATION

    duration = prefs.get("duration", "Any")

    is_movie = movies["type"] == "Movie"
    is_show = movies["type"] == "TV Show"

    if duration == "Short (under 90 minutes)":

        keep &= (
            (is_movie & (movies["number"] < 90))
            | (is_show & (movies["number"] == 1))
        )

    elif duration == "Medium (90–120 minutes)":

        keep &= (
            (is_movie & movies["number"].between(90, 120))
            | (is_show & movies["number"].between(2, 3))
        )

    elif duration == "Long (over 120 minutes)":

        keep &= (
            (is_movie & (movies["number"] > 120))
            | (is_show & (movies["number"] >= 4))
        )

    return movies[keep]


# ==========================================
# 10. GENERATE RECOMMENDATIONS
# ==========================================

def get_recommendations(prefs):

    try:

        count = int(prefs.get("count", 3))

    except (TypeError, ValueError):

        count = 3

    if count not in (3, 5):
        count = 3

    # APPLY FILTERS

    candidates = filter_movies(prefs)

    if candidates.empty:
        return []

    # GET SELECTED GENRES

    genres = prefs.get("genres", [])

    if not isinstance(genres, list):
        genres = []

    query = " ".join(
        GENRE_WORDS[genre]
        for genre in genres
        if genre in GENRE_WORDS
    )

    # NO GENRE SELECTED

    if not query:

        best = candidates.sample(
            n=min(count, len(candidates)),
            random_state=None
        )

    else:

        # CONVERT USER PREFERENCES INTO TF-IDF

        query_vector = vectorizer.transform(
            [query]
        )

        candidate_vectors = tfidf_matrix[
            candidates.index
        ]

        # CALCULATE COSINE SIMILARITY

        scores = cosine_similarity(
            query_vector,
            candidate_vectors
        ).flatten()

        candidates = candidates.copy()

        candidates["score"] = scores

        best = candidates.sort_values(
            by="score",
            ascending=False
        ).head(count)

    # PREPARE RESULTS

    results = []

    for _, row in best.iterrows():

        results.append({

            "title": row["title"],

            "type": row["type"],

            "year": int(row["release_year"]),

            "rating": row["rating"] or "Not rated",

            "duration": row["duration"],

            "genres": row["listed_in"],

            "country": row["country"],

            "cast": ", ".join(
                row["cast"].split(", ")[:4]
            ),

            "description": row["description"]

        })

    return results
