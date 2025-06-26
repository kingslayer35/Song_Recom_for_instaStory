from flask import Flask, render_template, request, jsonify
import pickle
import requests
import json
import time
import os
from description import rank_songs, process_image

app = Flask(__name__)

# Load precomputed song data once at startup
with open('song_data.pkl', 'rb') as f:
    precomputed_song_data = pickle.load(f)

# Securely fetch API keys from environment variables
SUNO_API_KEY = os.getenv("SUNO_API_KEY")  # Optional, may be None
ELEVENLABS_API_KEY = "sk_5ece95f1d93013ead65918058750c451e1000aadd9979c5e"

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

######################
# OLD FEATURE: SONG RECOMMENDATION FROM IMAGE
######################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    # Check for the uploaded image file
    if 'photo' not in request.files:
        return jsonify({'error': 'Missing image file.'}), 400
    file = request.files['photo']
    if file.filename == "":
        return jsonify({'error': 'No selected file.'}), 400

    # Get the optional manual description from the form
    manual_description = request.form.get('manual_description', "").strip()
    
    # Get selected language filters and artist filters
    selected_languages = request.form.getlist('languages')
    selected_artists = request.form.getlist('artists')
    
    # Process the image using BLIP + Gemini to get refined description
    refined_description = process_image(file, manual_description)
    
    # Filter the precomputed song data by language and artists if selected
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
    
    # Rank songs using the refined description and filtered data
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


######################
# NEW FEATURE: LYRICS + AUDIO GENERATION FROM IMAGE DESCRIPTION
######################

def generate_lyrics_with_gemini(image_description, mood, genre="pop", language="English"):

    import google.generativeai as genai
    GEMINI_API_KEY = 'AIzaSyC2KQPEjT-RDGoQwFJW2pgryK7gjr_ueqo'
    genai.configure(api_key=GEMINI_API_KEY)

    try:
        print("⏳ Generating lyrics using Gemini...")
        prompt = f"""
You are a professional songwriter.

Generate original lyrics based on this image description:
"{image_description}"

Requirements:
- Genre: {genre}
- Mood: {mood}
- Language: {language}
- Family-friendly and emotional
- Structure: Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus
- Length: 2–3 minutes worth of singing

Format strictly as:
[Verse 1]
...

[Chorus]
...

and so on.
"""
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None

def generate_audio_with_elevenlabs(lyrics, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """
    Generate spoken audio using ElevenLabs Text-to-Speech API.
    Note: voice_id can be changed as per your ElevenLabs voices.
    """
    try:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": lyrics,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", json=data, headers=headers)
        
        if response.status_code == 200:
            audio_filename = f"generated_audio_{int(time.time())}.mp3"
            audio_path = os.path.join("static", "audio", audio_filename)
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return f"/static/audio/{audio_filename}"
        else:
            print(f"ElevenLabs API error: {response.status_code} {response.text}")
            return None
            
    except Exception as e:
        print(f"Error generating audio with ElevenLabs: {e}")
        return None



@app.route('/generate_song', methods=['POST'])
def generate_song():
    """
    Endpoint to generate custom lyrics and audio based on image description
    """
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

        # Step 1: Generate lyrics using Gemini instead of OpenAI
        lyrics = generate_lyrics_with_gemini(image_description, mood, genre, language)
        if not lyrics:
            print("❌ Failed to generate lyrics from Gemini")
            return jsonify({'error': 'Failed to generate lyrics'}), 500

        print("✅ Lyrics generation complete.")

        # Step 2: Generate audio (spoken version using ElevenLabs)
        print("🎧 Generating audio with ElevenLabs...")
        audio_url = generate_audio_with_elevenlabs(lyrics)

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

######################
# Extra endpoints for UI options
######################

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
