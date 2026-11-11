
from flask import Flask, render_template, request, jsonify

from recommendation import get_recommendations


# ==========================================
# 1. INITIALIZE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# 2. HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# 3. RECOMMENDATION API
# ==========================================

@app.route("/recommend", methods=["POST"])
def recommend():

    try:

        # RECEIVE USER PREFERENCES
        preferences = request.get_json(silent=True)

        if not isinstance(preferences, dict):
            return jsonify({
                "error": "Invalid preferences received."
            }), 400

        # VALIDATE CONTENT TYPE
        allowed_types = [
            "Movies",
            "TV Shows",
            "Both"
        ]

        if preferences.get("type") not in allowed_types:
            return jsonify({
                "error": "Invalid content type."
            }), 400

        # VALIDATE GENRES
        allowed_genres = [
            "Action",
            "Comedy",
            "Drama",
            "Romance",
            "Thriller",
            "Horror",
            "Sci-Fi",
            "Fantasy",
            "Documentary"
        ]

        genres = preferences.get("genres", [])

        if (
            not isinstance(genres, list)
            or len(genres) > 3
            or any(genre not in allowed_genres for genre in genres)
        ):
            return jsonify({
                "error": "Invalid genre selection."
            }), 400

        # VALIDATE INDUSTRY
        allowed_industries = [
            "Any",
            "Hollywood",
            "Bollywood",
            "Korean",
            "Japanese",
            "Other / International"
        ]

        if preferences.get("industry") not in allowed_industries:
            return jsonify({
                "error": "Invalid film industry."
            }), 400

        # VALIDATE RELEASE YEAR
        allowed_years = [
            "Any",
            "2020–2026",
            "2010–2019",
            "2000–2009",
            "Before 2000"
        ]

        if preferences.get("year") not in allowed_years:
            return jsonify({
                "error": "Invalid release year."
            }), 400

        # VALIDATE AUDIENCE
        allowed_audiences = [
            "Under 18",
            "Adult (18+)"
        ]

        if preferences.get("audience") not in allowed_audiences:
            return jsonify({
                "error": "Invalid audience selection."
            }), 400

        # VALIDATE DURATION
        allowed_durations = [
            "Any",
            "Short (under 90 minutes)",
            "Medium (90–120 minutes)",
            "Long (over 120 minutes)"
        ]

        if preferences.get("duration") not in allowed_durations:
            return jsonify({
                "error": "Invalid duration selection."
            }), 400

        # VALIDATE RECOMMENDATION COUNT
        if preferences.get("count") not in [3, 5]:
            return jsonify({
                "error": "Choose either 3 or 5 recommendations."
            }), 400

        # GENERATE RECOMMENDATIONS
        movies = get_recommendations(preferences)

        return jsonify({
            "recommendations": movies
        })

    except Exception as error:

        app.logger.exception(
            "Recommendation generation failed."
        )

        return jsonify({
            "error": "Unable to generate recommendations. Please try again."
        }), 500


# ==========================================
# 4. RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
