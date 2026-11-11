# Netflix Recommendation System

## Project Description

A content-based Netflix movie and TV show recommendation system built using Python, Flask, TF-IDF and Cosine Similarity.

## Technologies Used

- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- HTML
- CSS
- TF-IDF
- Cosine Similarity

## Features

1. Genre preferences
2. Country/region preference
3. Release year filtering
4. Age rating filtering
5. Duration filtering
6. Movie and TV show selection
7. Content-based recommendations
8. Similar title recommendations
9. Responsive web interface

## Installation

Install the required libraries:

pip install -r requirements.txt

## Dataset

Place your Netflix dataset in the project root folder.

The filename must be:

netflix_titles.csv

The dataset should contain these columns:

show_id, type, title, director, cast, country, release_year, rating, duration, listed_in, description

## Run the Project

Open the VS Code terminal and execute:

python app.py

Open your browser:

http://127.0.0.1:5000

## Recommendation Algorithm

TF-IDF converts movie descriptions and metadata into numerical vectors.

Cosine Similarity compares these vectors to identify relevant titles based on user preferences.

## Project Structure

Netflix_Recommendation/
- netflix_titles.csv
- recommendation.py
- app.py
- requirements.txt
- README.txt
- templates/index.html
- static/style.css