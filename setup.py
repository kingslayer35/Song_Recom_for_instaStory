"""
Setup script for Song Recommender project
Run this after installing requirements to initialize the application
"""
import os
import secrets
import sys


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if os.path.exists('.env'):
        print("[OK] .env file already exists")
        return

    if not os.path.exists('.env.example'):
        print("[ERROR] .env.example not found!")
        return

    # Read example file
    with open('.env.example', 'r') as f:
        content = f.read()

    # Generate a random secret key
    secret_key = secrets.token_hex(32)
    content = content.replace('your_secret_key_here_generate_with_python_secrets', secret_key)

    # Write to .env
    with open('.env', 'w') as f:
        f.write(content)

    print("[OK] Created .env file with generated SECRET_KEY")
    print("[WARNING] IMPORTANT: Edit .env and add your GEMINI_API_KEY")


def create_directories():
    """Create necessary directories"""
    directories = [
        'static/uploads',
        'static/audio'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create .gitkeep to preserve empty directories
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            open(gitkeep_path, 'a').close()

    print("[OK] Created necessary directories")


def check_song_data():
    """Check if song_data.pkl exists"""
    if os.path.exists('song_data.pkl'):
        print("[OK] song_data.pkl found")
    else:
        print("[WARNING] song_data.pkl not found - run model.ipynb to generate it")


def main():
    """Run all setup tasks"""
    print("=" * 60)
    print("Song Recommender - Setup Script")
    print("=" * 60)
    print()

    create_env_file()
    create_directories()
    check_song_data()

    print()
    print("=" * 60)
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Edit .env and add your GEMINI_API_KEY from https://aistudio.google.com/app/apikey")
    print("2. If song_data.pkl is missing, run: jupyter notebook model.ipynb")
    print("3. Run the application: python app.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
