import os
import time
import logging
import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from trendspy import Trends

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
OMDB_API_KEY = "c0c5b16c"
MOVIES_PATH = "data/movies.xlsx"
DATABASE_PATH = "output/database.xlsx"
VISUALIZATION_PATH = "output/visualizations/"
OUTPUT_PATH = "output/"

# Ensure directories exist
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(VISUALIZATION_PATH, exist_ok=True)

# Initialize TrendsPy
tr = Trends(request_delay=10.7)

def fetch_omdb_data(title):
    """Fetch movie data from OMDB API."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            return {
                "Title": data.get("Title", ""), "Year": data.get("Year", ""), "Rated": data.get("Rated", ""),
                "Runtime": data.get("Runtime", ""), "imdbRating": data.get("imdbRating", ""),
                "imdbVotes": data.get("imdbVotes", ""), "BoxOffice": data.get("BoxOffice", ""),
                "Released": data.get("Released", ""), "Genre": data.get("Genre", ""),
                "Awards": data.get("Awards", ""), "Metascore": data.get("Metascore", ""),
                "Ratings": data.get("Ratings", "")
            }
        logging.error(f"Failed to fetch data for movie: {title}. Error: {data.get('Error', 'Unknown error')}")
        return None
    except requests.RequestException as e:
        logging.error(f"Request failed for movie: {title}. Error: {str(e)}")
        return None

def fetch_googletrends_data(movie):
    """Fetch Google Trends data for a movie."""
    title = movie["Title"].replace(":", "")
    release_date = movie["Released"]
    try:
        release_datetime = datetime.strptime(release_date, "%d %b %Y")
        timeframe = f'{(release_datetime + relativedelta(years=1)).strftime("%Y-%m-%d")} 1-y'
        interest_data = tr.interest_over_time(title, timeframe=timeframe)
        return interest_data[title].sum() if not interest_data.empty else None
    except Exception as e:
        logging.error(f"Error fetching Google Trends data for movie: {title}. Error: {str(e)}")
        return None

def load_movie_list():
    """Load the movie list from an Excel file."""
    return pd.read_excel(MOVIES_PATH)

def append_to_database(df):
    """Append new rows to the database without overwriting existing data."""
    if os.path.exists(DATABASE_PATH):
        existing_df = pd.read_excel(DATABASE_PATH)
        updated_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates()
    else:
        updated_df = df
    updated_df.to_excel(DATABASE_PATH, index=False)

def process_movies(movies_list):
    """Fetch and process OMDB and Google Trends data."""
    omdb_data_list, googletrends_data_list = [], []
    database_df = pd.read_excel(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else pd.DataFrame(columns=['Title'])
    
    for _, row in tqdm(movies_list.iterrows(), total=len(movies_list), desc="Fetching OMDB Data"):
        title = row["title"]
        if title in database_df['Title'].values:
            continue
        omdb_data = fetch_omdb_data(title)
        logging.info(f"Fetching omdb data for new movie: {title}")
        if omdb_data:
            omdb_data_list.append(omdb_data)
        time.sleep(1)
    
    omdb_df = pd.DataFrame(omdb_data_list)
    omdb_df_after_2006 = omdb_df[pd.to_numeric(omdb_df["Year"], errors='coerce') >= 2006]
    
    for _, row in tqdm(omdb_df_after_2006.iterrows(), total=len(omdb_df_after_2006), desc="Fetching Google Trends Data"):
        title = row["Title"]
        if title in database_df['Title'].values:
            continue
        googletrends_data = fetch_googletrends_data(row)
        logging.info(f"Fetching google trends data for new movie: {title}")
        if googletrends_data:
            googletrends_data_list.append({"Title": title, "GoogleSearches": googletrends_data})
    
    googletrends_df = pd.DataFrame(googletrends_data_list)
    merged_df = omdb_df.merge(googletrends_df, on="Title", how="left").fillna("N/A")
    return merged_df

def main():
    """Main function to run the automation process."""
    movies_list = load_movie_list()
    merged_df = process_movies(movies_list)
    movies_df = transform_data(merged_df)
    logging.info("Saving new data into database")
    append_to_database(movies_df)
    logging.info("Processing complete. Data saved successfully.")

if __name__ == "__main__":
    main()
