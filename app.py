# app.py
from flask import Flask, render_template, request, jsonify
import pickle
import os
import asyncio
from description import rank_songs, process_image
from suno_session_manager import generate_song_on_suno
from suno_automation import automate_login

app = Flask(__name__)

# Load precomputed song data once at startup
with open('song_data.pkl', 'rb') as f:
    precomputed_song_data = pickle.load(f)

# Mapping from artist name to language category
artist_language = {
    "Sachin-Jigar": "Hindi",
    "The Weeknd": "English",
    "Udit Narayan": "Hindi",
    "Atif Aslam": "Hindi",
    "Taylor Swift": "English",
    "Karan Aujla": "Punjabi",
    "Drake": "English",
    "Tanishk Bagchi": "Hindi",
    "Diljit Dosanjh": "Punjabi",
    "Masoom Sharma": "Haryanvi",
    "Bruno Mars": "English",
    "Vishal Mishra": "Hindi",
    "G. V. Prakash": "Tamil",
    "SZA": "English",
    "Sidhu Moose Wala": "Punjabi",
    "Billie Eilish": "English",
    "Rahat Fateh Ali Khan": "Hindi",
    "Lady Gaga": "English",
    "Darshan Raval": "Hindi",
    "Sachet Tandon": "Hindi",
    "Manoj Muntashir": "Hindi",
    "Pawan Singh": "Bhojpuri",
    "Gur Sidhu": "Punjabi",
    "Jimin": "English",
    "Arjan Dhillon": "Punjabi",
    "AP Dhillon": "Punjabi",
    "Javed Ali": "Hindi",
    "Justin Bieber": "English",
    "Lana Del Rey": "English",
    "Thaman S": "Telugu",
    "Cheema Y": "Punjabi",
    "Jaani": "Hindi",
    "Ariana Grande": "English"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'Missing image file.'}), 400
    file = request.files['photo']
    if file.filename == "":
        return jsonify({'error': 'No selected file.'}), 400

    manual_description = request.form.get('manual_description', "").strip()
    selected_languages = request.form.getlist('languages')
    selected_artists = request.form.getlist('artists')

    refined_description = process_image(file, manual_description)

    filtered_data = precomputed_song_data
    if selected_languages:
        filtered_data = [
            song for song in filtered_data
            if artist_language.get(song['artist'], "Other") in selected_languages
        ]
    if selected_artists:
        filtered_data = [
            song for song in filtered_data
            if song['artist'] in selected_artists
        ]

    ranked = rank_songs(refined_description, filtered_data, top_n=5)
    recommendations = [{
        'artist': song['artist'],
        'track': song['track'],
        'description': song.get('description', 'No description available.'),
        'similarity': float(sim)
    } for song, sim in ranked]

    return jsonify({
        'refined_description': refined_description,
        'recommendations': recommendations
    })

def generate_lyrics_with_gemini(image_description, mood, genre="pop", language="English"):
    import google.generativeai as genai
    GEMINI_API_KEY = 'AIzaSyC2KQPEjT-RDGoQwFJW2pgryK7gjr_ueqo'
    genai.configure(api_key=GEMINI_API_KEY)

    try:
        print("⏳ Generating lyrics using Gemini...")

        prompt = f"""
You are a professional songwriter.

Write a short and meaningful {mood} {genre} song in {language}, based on this image description:
"{image_description}"

Requirements:
- Family-friendly and emotional tone
- Use common, singable language
- Total length must be LESS than 270 characters
- Format strictly as:
[Verse 1]
...

[Chorus]
...
"""

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)

        lyrics = response.text.strip()
        return lyrics

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None

@app.route('/generate_song', methods=['POST'])
def generate_song():
    try:
        print("\n--- [GENERATE SONG REQUEST RECEIVED] ---")
        data = request.get_json()
        image_description = data.get('description', '')
        mood = data.get('mood', 'happy')
        genre = data.get('genre', 'pop')
        language = data.get('language', 'English')

        print(f"> Input Description: {image_description}")
        print(f"> Mood: {mood} | Genre: {genre} | Language: {language}")

        if not image_description:
            return jsonify({'error': 'Image description is required'}), 400

        lyrics = generate_lyrics_with_gemini(image_description, mood, genre, language)
        if not lyrics:
            print("❌ Failed to generate lyrics from Gemini")
            return jsonify({'error': 'Failed to generate lyrics'}), 500

        print("✅ Lyrics generation complete.")

        # Check if session file exists and is valid
        session_file = "suno_session.json"
        if not os.path.exists(session_file) or os.path.getsize(session_file) < 100:
            print("🔒 No valid Suno session found. Initiating login...")
            asyncio.run(automate_login())

        print("🎧 Generating audio with Suno...")
        audio_url = asyncio.run(generate_song_on_suno(lyrics))

        if not audio_url:
            print("⚠️ Audio generation failed — returning lyrics only")
            return jsonify({
                'lyrics': lyrics,
                'audio_url': None,
                'message': 'Audio generation unavailable - lyrics only'
            })

        print(f"✅ Audio file created: {audio_url}")

        return jsonify({
            'lyrics': lyrics,
            'audio_url': audio_url,
            'message': 'Song generated successfully!'
        })

    except Exception as e:
        print(f"🔥 Server error: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/get_song_moods', methods=['GET'])
def get_song_moods():
    moods = [
        'happy', 'sad', 'energetic', 'calm', 'romantic', 
        'nostalgic', 'uplifting', 'melancholic', 'dramatic', 'peaceful'
    ]
    return jsonify({'moods': moods})

@app.route('/get_song_genres', methods=['GET'])
def get_song_genres():
    genres = [
        'pop', 'rock', 'hip-hop', 'country', 'jazz', 'blues', 
        'folk', 'electronic', 'classical', 'indie', 'r&b', 'reggae'
    ]
    return jsonify({'genres': genres})

if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True)
