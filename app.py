# app.py
from flask import Flask, render_template, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import pickle
import os
import asyncio
import logging
import time
from functools import lru_cache
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from description import rank_songs, process_image, init_models
from suno_session_manager import generate_song_on_suno
from suno_automation import automate_login
from cache_utils import description_cache, get_image_hash

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

# CSRF Protection
csrf = CSRFProtect(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    enabled=os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
)

# Allowed file extensions
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,webp').split(','))

# Load precomputed song data once at startup
logger.info("Loading song data...")
try:
    with open('song_data.pkl', 'rb') as f:
        precomputed_song_data = pickle.load(f)
    logger.info(f"Loaded {len(precomputed_song_data)} songs")
except Exception as e:
    logger.error(f"Failed to load song data: {e}")
    precomputed_song_data = []

# Initialize BLIP and Sentence Transformer models at startup
logger.info("Initializing AI models...")
try:
    init_models()
    logger.info("Models initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize models: {e}")

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

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def start_timer():
    """Start request timer for performance monitoring"""
    g.start_time = time.time()

@app.after_request
def log_request(response):
    """Log request details and response time"""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        logger.info(f"{request.method} {request.path} - {response.status_code} - {elapsed:.3f}s")
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_photo', methods=['POST'])
@limiter.limit("10 per minute")
def upload_photo():
    try:
        if 'photo' not in request.files:
            logger.warning("Upload attempt without photo file")
            return jsonify({'error': 'Missing image file.'}), 400

        file = request.files['photo']
        if file.filename == "":
            logger.warning("Upload attempt with empty filename")
            return jsonify({'error': 'No selected file.'}), 400

        # Validate file extension
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type attempted: {file.filename}")
            return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Secure the filename
        filename = secure_filename(file.filename)
        logger.info(f"Processing upload: {filename}")

        manual_description = request.form.get('manual_description', "").strip()
        selected_languages = request.form.getlist('languages')
        selected_artists = request.form.getlist('artists')

        # Try to get from cache first
        cache_key = get_image_hash(file) + (f"_{manual_description}" if manual_description else "")
        cached_description = description_cache.get(cache_key)

        if cached_description:
            logger.info(f"Using cached description (cache size: {description_cache.size()})")
            refined_description = cached_description
        else:
            # Process image with error handling
            try:
                refined_description = process_image(file, manual_description)
                logger.info(f"Image processed successfully: {len(refined_description)} chars")

                # Cache the result
                description_cache.set(cache_key, refined_description)
                logger.info(f"Cached description (cache size: {description_cache.size()})")
            except Exception as e:
                logger.error(f"Image processing error: {e}", exc_info=True)
                return jsonify({'error': 'Failed to process image. Please try again.'}), 500

        # Filter songs based on user preferences
        filtered_data = precomputed_song_data
        if selected_languages:
            filtered_data = [
                song for song in filtered_data
                if artist_language.get(song['artist'], "Other") in selected_languages
            ]
            logger.info(f"Filtered to {len(filtered_data)} songs by language")

        if selected_artists:
            filtered_data = [
                song for song in filtered_data
                if song['artist'] in selected_artists
            ]
            logger.info(f"Filtered to {len(filtered_data)} songs by artist")

        if not filtered_data:
            return jsonify({'error': 'No songs match your filters. Please adjust your selection.'}), 400

        # Rank songs by similarity
        try:
            ranked = rank_songs(refined_description, filtered_data, top_n=5)
            recommendations = [{
                'artist': song['artist'],
                'track': song['track'],
                'description': song.get('description', 'No description available.'),
                'similarity': float(sim)
            } for song, sim in ranked]
            logger.info(f"Returning {len(recommendations)} recommendations")
        except Exception as e:
            logger.error(f"Ranking error: {e}", exc_info=True)
            return jsonify({'error': 'Failed to generate recommendations. Please try again.'}), 500

        return jsonify({
            'refined_description': refined_description,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"Unexpected error in upload_photo: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

def generate_lyrics_with_gemini(image_description, mood, genre="pop", language="English"):
    """Generate song lyrics using Google Gemini AI"""
    import google.generativeai as genai

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY not configured. Please set it in your .env file")

    genai.configure(api_key=GEMINI_API_KEY)

    try:
        logger.info(f"Generating lyrics: mood={mood}, genre={genre}, language={language}")

        prompt = f"""
You are a professional songwriter.

Write a short and meaningful {mood} {genre} song in {language}, based on this image description:
"{image_description}"

Requirements:
- Family-friendly and emotional tone
- Use common, singable language
- Total length must be LESS than 250 characters
- Format strictly as:
[Verse 1]
...

[Chorus]
...
"""

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)

        lyrics = response.text.strip()
        logger.info(f"Lyrics generated successfully: {len(lyrics)} chars")
        return lyrics

    except Exception as e:
        logger.error(f"Gemini lyrics generation error: {e}", exc_info=True)
        return None

@app.route('/generate_song', methods=['POST'])
@limiter.limit("5 per minute")
def generate_song():
    try:
        logger.info("Generate song request received")
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid request data'}), 400

        image_description = data.get('description', '')
        mood = data.get('mood', 'happy')
        genre = data.get('genre', 'pop')
        language = data.get('language', 'English')

        logger.info(f"Song params - Mood: {mood}, Genre: {genre}, Language: {language}")

        if not image_description:
            logger.warning("Generate song called without description")
            return jsonify({'error': 'Image description is required'}), 400

        # Generate lyrics
        try:
            lyrics = generate_lyrics_with_gemini(image_description, mood, genre, language)
            if not lyrics:
                logger.error("Lyrics generation returned None")
                return jsonify({'error': 'Failed to generate lyrics'}), 500
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Lyrics generation failed: {e}", exc_info=True)
            return jsonify({'error': 'Failed to generate lyrics. Please try again.'}), 500

        # Check if session file exists and is valid
        session_file = "suno_session.json"
        if not os.path.exists(session_file) or os.path.getsize(session_file) < 100:
            logger.info("No valid Suno session found. Initiating login...")
            try:
                asyncio.run(automate_login())
            except Exception as e:
                logger.error(f"Suno login failed: {e}", exc_info=True)
                return jsonify({
                    'lyrics': lyrics,
                    'audio_url': None,
                    'message': 'Audio generation unavailable - lyrics only'
                })

        # Generate audio with Suno
        try:
            logger.info("Generating audio with Suno...")
            audio_url = asyncio.run(generate_song_on_suno(lyrics))

            if not audio_url:
                logger.warning("Audio generation returned no URL")
                return jsonify({
                    'lyrics': lyrics,
                    'audio_url': None,
                    'message': 'Audio generation unavailable - lyrics only'
                })

            logger.info(f"Audio file created: {audio_url}")
            return jsonify({
                'lyrics': lyrics,
                'audio_url': audio_url,
                'message': 'Song generated successfully!'
            })

        except Exception as e:
            logger.error(f"Audio generation error: {e}", exc_info=True)
            return jsonify({
                'lyrics': lyrics,
                'audio_url': None,
                'message': 'Audio generation unavailable - lyrics only'
            })

    except Exception as e:
        logger.error(f"Unexpected error in generate_song: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

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
