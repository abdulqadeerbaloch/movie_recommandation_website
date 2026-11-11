
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("preference-form");
    const submitBtn = document.getElementById("submit-btn");
    const genreCount = document.getElementById("genre-count");
    const resultsSection = document.getElementById("results-section");
    const moviesContainer = document.getElementById("movies-container");
    const resultsMessage = document.getElementById("results-message");
    const errorMessage = document.getElementById("error-message");
    const restartBtn = document.getElementById("restart-btn");

    // Update selected genre count
    const genreCheckboxes = document.querySelectorAll(
        'input[name="genres"]'
    );

    function updateGenreCount() {
        const selected = document.querySelectorAll(
            'input[name="genres"]:checked'
        );

        genreCount.textContent = selected.length;
    }

    genreCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const selected = document.querySelectorAll(
                'input[name="genres"]:checked'
            );

            if (selected.length > 3) {
                checkbox.checked = false;
                alert("You can select a maximum of 3 genres.");
            }

            updateGenreCount();
        });
    });

    updateGenreCount();

    // Display recommendations
    function displayRecommendations(recommendations) {
        moviesContainer.innerHTML = "";

        if (!recommendations || recommendations.length === 0) {
            resultsMessage.textContent =
                "No matching recommendations were found. Try changing your preferences.";
            return;
        }

        resultsMessage.textContent =
            `We found ${recommendations.length} recommendations for you.`;

        recommendations.forEach((movie) => {
            const card = document.createElement("article");
            card.className = "movie-card";

            const title = document.createElement("h3");
            title.textContent = movie.title || "Untitled";

            const meta = document.createElement("div");
            meta.className = "movie-meta";

            const details = [
                movie.type,
                movie.year,
                movie.rating,
                movie.duration,
                movie.country
            ];

            details.forEach((detail) => {
                if (detail !== undefined && detail !== null && detail !== "") {
                    const span = document.createElement("span");
                    span.textContent = detail;
                    meta.appendChild(span);
                }
            });

            const description = document.createElement("p");
            description.className = "movie-description";
            description.textContent =
                movie.description || "No description available.";

            card.appendChild(title);
            card.appendChild(meta);

            if (movie.genres) {
                const genres = document.createElement("p");
                genres.className = "movie-description";
                genres.textContent = "Genres: " + movie.genres;
                card.appendChild(genres);
            }

            card.appendChild(description);
            moviesContainer.appendChild(card);
        });
    }

    // Submit all preferences together
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        errorMessage.textContent = "";
        resultsMessage.textContent = "";
        moviesContainer.innerHTML = "";

        const formData = new FormData(form);

        const preferences = {
            type: formData.get("type"),
            genres: formData.getAll("genres"),
            industry: formData.get("industry"),
            year: formData.get("year"),
            audience: formData.get("audience"),
            duration: formData.get("duration"),
            count: Number(formData.get("count"))
        };

        submitBtn.disabled = true;
        submitBtn.textContent = "Finding Recommendations...";

        try {
            const response = await fetch("/recommend", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(preferences)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to get recommendations."
                );
            }

            displayRecommendations(data.recommendations);

            resultsSection.hidden = false;

            resultsSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            console.error("Recommendation error:", error);
            errorMessage.textContent =
                error.message || "Something went wrong. Please try again.";
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Find My Recommendations →";
        }
    });

    // Start again
    restartBtn.addEventListener("click", () => {
        form.reset();
        updateGenreCount();

        resultsSection.hidden = true;
        moviesContainer.innerHTML = "";
        resultsMessage.textContent = "";
        errorMessage.textContent = "";

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
});
