# 🎵 Image Song Recommender

<div align="center">
  <img src="static/uploads/Screenshot 2025-07-04 at 8.02.00 PM.png" width="600" alt="Image Song Recommender Interface">
  
  **Transform images into personalized music experiences with AI-powered song recommendations and custom audio generation**
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
</div>

---

## 🌟 Overview

Image Song Recommender is a cutting-edge Flask web application that bridges visual aesthetics with musical experiences. By analyzing uploaded images, it generates personalized song recommendations and can even create entirely new songs tailored to the mood and atmosphere captured in your photos.

### 🎯 Key Highlights
- **AI-Powered Analysis**: Combines BLIP image captioning with Google Gemini for deep contextual understanding
- **Smart Recommendations**: Semantic similarity matching against a curated song database
- **Custom Song Creation**: Generate unique lyrics and audio using Gemini + Suno.ai
- **Interactive Interface**: Modern, responsive web design with real-time filtering

---

## ✨ Features

### 🖼️ **Intelligent Image Analysis**
- Upload any image and receive detailed AI-generated descriptions
- Combines BLIP captioning with Gemini's contextual analysis
- Optional manual description input for enhanced personalization

### 🎵 **Personalized Recommendations**
- Semantic similarity matching using Sentence Transformers
- Curated song database with precomputed embeddings
- Advanced filtering by language and artist preferences

### 🎼 **Custom Song Generation**
- AI-generated lyrics tailored to your image's mood
- Professional audio creation via Suno.ai integration
- Downloadable audio files for personal use

### 🎨 **Modern Interface**
- Interactive filters and animated loading states
- Clear error handling and user feedback

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask |
| **Image Processing** | BLIP (Salesforce/blip-image-captioning-base) |
| **AI Generation** | Google Gemini API |
| **Recommendations** | Sentence Transformers (`all-mpnet-base-v2`) |
| **Audio Creation** | Suno.ai |
| **Browser Automation** | Playwright |
| **Data Processing** | Pandas, Pickle |
| **Frontend** | HTML5, CSS3, JavaScript |

---

## 📁 Project Structure

```
image-song-recommender/
├── 📁 static/
│   ├── 🎵 audio/              # Generated audio files
│   └── 📷 uploads/            # Temporary image storage
├── 📁 templates/
│   └── 🌐 index.html          # Main web interface
├── 🐍 app.py                  # Flask application core
├── 🧠 description.py          # AI processing logic
├── 📊 model.ipynb             # Data processing notebook
├── 📋 requirements.txt        # Dependencies
├── 📄 song_data.csv          # Raw song metadata
├── 💾 song_data.pkl          # Precomputed embeddings
├── 🤖 suno_automation.py     # Suno.ai login automation
└── 🔧 suno_session_manager.py # Suno.ai session management
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Internet connection for AI services

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ish4722/Song_Recom_for_instaStory.git
   cd Song_Recom_for_instaStory
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install  # Download browser binaries
   ```

4. **Configure API key**
   
   ⚠️ **Important**: Replace the placeholder API key in both `app.py` and `description.py`:
   ```python
   GEMINI_API_KEY = 'YOUR_ACTUAL_GEMINI_API_KEY_HERE'
   ```
   
   Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

5. **Verify song data**
   
   Ensure `song_data.pkl` exists in the root directory. If missing, run the `model.ipynb` notebook to generate it.

### Running the Application

```bash
python app.py
```

Navigate to `http://127.0.0.1:5000/` in your browser.

---

## 🎯 Usage Guide

### 1. Upload & Analyze
- **Upload an image** by clicking the file input or dragging and dropping
- **Add context** with an optional manual description
- **Set preferences** using language and artist filters

### 2. Get Recommendations
- Click "Get Song Recommendations"
- View the AI-generated image description
- Explore ranked song suggestions with similarity scores

### 3. Generate Custom Songs
- Click "Generate Song from This Description"
- Wait for AI-powered lyrics generation
- **Important**: Don't close the Playwright browser window during Suno.ai login
- Complete any security challenges (CAPTCHA) when prompted
- Download your unique custom song

---

## ⚙️ Configuration

### Gemini API Setup
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate your API key
3. Replace the placeholder in `app.py` and `description.py`

### Suno.ai Authentication
- First-time users will see an automated login browser window
- Complete the Google login process manually
- Don't close the window until login is confirmed
- Session will be saved for future use

---

## 🔮 Roadmap

- [ ] **Song recommendation for Videos** -Improve Range of usage
- [ ] **Enhanced Mobile Experience** - Improved responsive design
- [ ] **User Accounts** - Save preferences and history
- [ ] **Audio Previews** - Spotify API integration for track previews
- [ ] **Advanced Filters** - Genre, mood, and era-based filtering
- [ ] **Batch Processing** - Multiple image analysis
- [ ] **Social Features** - Share recommendations and custom songs

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[BLIP](https://github.com/salesforce/BLIP)** - Revolutionary image captioning technology
- **[Google Gemini](https://ai.google.dev/)** - Advanced AI for description refinement and lyrics generation
- **[Suno.ai](https://suno.ai/)** - AI-powered music generation platform
- **[Sentence Transformers](https://www.sbert.net/)** - Efficient semantic similarity matching
- **[Playwright](https://playwright.dev/)** - Reliable browser automation

---

<div align="center">
  <p>Made with ❤️ by Garv</p>
  <p>
    <a href="https://github.com/ish4722/Song_Recom_for_instaStory/issues">Report Bug</a>
    ·
    <a href="https://github.com/ish4722/Song_Recom_for_instaStory/issues">Request Feature</a>
  </p>
</div>
