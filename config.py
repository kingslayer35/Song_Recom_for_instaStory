"""
Configuration settings for the Song Recommendation application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB

    # File upload settings
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,webp').split(','))
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    AUDIO_FOLDER = os.path.join('static', 'audio')

    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))

    # Model settings
    SONG_DATA_FILE = 'song_data.pkl'
    SENTENCE_TRANSFORMER_MODEL = 'all-mpnet-base-v2'
    BLIP_MODEL_NAME = 'Salesforce/blip-image-captioning-base'

    # Cache settings
    CACHE_ENABLED = True
    CACHE_MAX_SIZE = 100  # Maximum number of cached descriptions

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
