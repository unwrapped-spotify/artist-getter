#### Perform required set up

# Load required libraries
import json                                                 # For working with JSON data
import spotipy                                              # Python wrapper for spotify API
from spotipy.oauth2 import SpotifyOAuth                     # Allows acessing user data for spotify API
import os                                                   # Used for setting environment variables
import pandas as pd                                         # For wrangling data
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_cache import FirestoreCacheHandler

load_dotenv()

# Load the api key
api_json = json.load(open("api-key.json"))

# Set environment variables as required by spotipy
os.environ["SPOTIPY_CLIENT_ID"] = api_json["client_id"]
os.environ["SPOTIPY_CLIENT_SECRET"] = api_json["client_secret"]
os.environ["SPOTIPY_REDIRECT_URI"] = api_json["redirect_uri"]

#### Get list of a users liked artists

# This scope is needed to read libraries
scope = "user-library-read"


cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred, {
    'projectId': os.environ["GCP_PROJECT_ID"]
})

db = firestore.client()

doc_ref = db.collection('users').document(os.environ["USER"])

# Authenticate with the spotify API
spotify_client = spotipy.Spotify(
    auth_manager = SpotifyOAuth(scope = scope, cache_handler = FirestoreCacheHandler(doc_ref)))

#print(SpotifyOAuth(scope = scope).get_cached_token())

#print(SpotifyOAuth(
#    scope = scope,
#    cache_handler = FirestoreCacheHandler(
#        os.environ["USER"], os.environ["GCP_PROJECT_ID"])).get_cached_token())

##spotify_client = spotipy.Spotify(auth = SpotifyOAuth(
##    scope = scope,
##    cache_handler = FirestoreCacheHandler(
##        os.environ["USER"], os.environ["GCP_PROJECT_ID"])).get_cached_token())

# These variables are used to loop through the users library until the end is reached
tracks_count = 50
i = 0

# Create an empty datafram to save the artist URIs in
artist_uri_df = pd.DataFrame(columns = ["artist"])

# Only 50 of the users tracks can be obtained at one time but the offset argument can allow the next 50 to be read.
# If 50 tracks are requested but less than 50 comeback then the entire library has been read
while tracks_count == 50:
    # Request 50 tracks
    tracks = spotify_client.current_user_saved_tracks(limit = 50, offset = i * 50)["items"]
    # See how many tracks were returned - this will break the loop if needed
    tracks_count = len(tracks)

    # Loop through the tracks received
    for track in tracks:
        # For each track, get the artists - there may be more than one, x ft. y for example
        # Getting additional artists may not be desired 
        artist_multiple = track["track"]["artists"]
        # Loop through the artists for a given track
        for artist in artist_multiple:
            # Get the uri
            artist_single_uri = artist["uri"]
            # Convert the uri to a data frame
            artist_single_uri_df = pd.DataFrame([artist_single_uri], columns = ["artist"])
            # Append the single artist to the full list
            artist_uri_df = artist_uri_df.append(artist_single_uri_df)
    # Increment i, this ensures the next 50 tracks are read in
    i += 1

# The dataframe produced above will have duplicated artists so make a unique list
artist_uri_unique = artist_uri_df["artist"].unique()

doc_ref.update({
    'artists_uri': artist_uri_unique.tolist(),
    'test': 'yes'
})