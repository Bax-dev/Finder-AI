from flask import Flask, request, jsonify, render_template
import requests
from difflib import SequenceMatcher

app = Flask(__name__)

#GENIUS_API_TOKEN = '' #GENIUS_API_TOKEN
BASE_URL = 'https://api.genius.com/'

def get_song_lyrics(artist_name):
    headers = {'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
    search_url = BASE_URL + 'search'
    params = {'q': artist_name}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code != 200:
        return []

    songs = []
    for hit in response.json()['response']['hits']:
        song_title = hit['result']['title']
        song_url = hit['result']['url']
        artist_name = hit['result']['primary_artist']['name']
        artist_image = hit['result']['primary_artist']['image_url'] if 'image_url' in hit['result']['primary_artist'] else None
        release_date = hit['result']['release_date'] if 'release_date' in hit['result'] else "Unknown"
        
        # Safely access the snippet field
        song_snippet = hit['result'].get('snippet', 'No snippet available')  # Default value if no snippet is found
        
        songs.append({
            'title': song_title,
            'url': song_url,
            'artist': artist_name,
            'image': artist_image,
            'release_date': release_date,
            'snippet': song_snippet  # Add snippet safely
        })
    return songs

def fetch_lyrics_from_url(song_url):
    # Placeholder for scraping lyrics from the URL (you can implement scraping here if needed)
    return "Lyrics of the song extracted from Genius"

def find_matching_song(input_lyrics, songs):
    best_match = None
    highest_similarity = 0

    for song in songs:
        snippet = song['snippet']
        similarity = SequenceMatcher(None, input_lyrics.lower(), snippet.lower()).ratio()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = song

    return best_match, highest_similarity

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    user_lyrics = data.get('lyrics', '')
    artist = data.get('artist', '')  # Artist name is optional

    if not user_lyrics:
        return jsonify({'error': 'Lyrics are required'}), 400

    # If artist name is provided, search with artist name; otherwise, search by lyrics only
    songs = get_song_lyrics(artist) if artist else get_song_lyrics('')
    match, similarity = find_matching_song(user_lyrics, songs)

    if match:
        return jsonify({
            'title': match['title'],
            'url': match['url'],
            'artist': match['artist'],
            'image': match['image'],
            'release_date': match['release_date'],
            'similarity': similarity
        })
    return jsonify({'error': 'No matching song found'}), 404


if __name__ == "__main__":
    app.run(debug=True)
