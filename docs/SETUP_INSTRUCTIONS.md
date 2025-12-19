# Setup Instructions

Quick guide to set up the improved Song Recommendation application.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Internet connection
- Google Gemini API key

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone and Navigate
```bash
git clone https://github.com/ish4722/Song_Recom_for_instaStory.git
cd Song_Recom_for_instaStory
```

### 2. Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 4. Run Setup Script
```bash
python setup.py
```

This will:
- ✅ Create `.env` file with auto-generated SECRET_KEY
- ✅ Create `static/uploads` and `static/audio` directories
- ✅ Check for `song_data.pkl`

### 5. Configure API Key

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

Edit `.env` file:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 6. Run Application
```bash
python app.py
```

Visit: http://127.0.0.1:5000

---

## 🔧 Configuration Options

### Environment Variables

Edit `.env` to customize:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Auto-generated (don't change)
SECRET_KEY=auto_generated_secret_key

# Optional (with defaults)
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=16777216  # 16MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=10
```

---

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not configured"
**Solution**: Edit `.env` and add your API key from Google AI Studio

### Issue: "song_data.pkl not found"
**Solution**: Run the Jupyter notebook to generate it:
```bash
jupyter notebook model.ipynb
```

### Issue: "Models not initialized"
**Solution**: The app loads models at startup. Check logs for errors:
```bash
tail -f app.log
```

### Issue: "Rate limit exceeded"
**Solution**: Wait 1 minute or adjust in `.env`:
```env
RATE_LIMIT_PER_MINUTE=20
```

### Issue: "File too large"
**Solution**: Increase limit in `.env`:
```env
MAX_CONTENT_LENGTH=33554432  # 32MB
```

---

## 📁 File Structure

After setup, you should have:

```
Song_Recom_for_instaStory/
├── .env                    # Your configuration (DO NOT COMMIT)
├── .env.example           # Template
├── .gitignore             # Git ignore rules
├── app.py                 # Main Flask application
├── description.py         # AI processing logic
├── cache_utils.py         # Caching utilities
├── config.py              # Configuration management
├── setup.py               # Setup automation script
├── requirements.txt       # Python dependencies
├── song_data.pkl          # Precomputed embeddings
├── song_data.csv          # Raw song data
├── static/
│   ├── uploads/           # Temporary image uploads
│   └── audio/             # Generated audio files
├── templates/
│   └── index.html         # Frontend
└── app.log                # Application logs
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Set strong SECRET_KEY in `.env`
- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `FLASK_DEBUG=False` in `.env`
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Never commit API keys to git
- [ ] Review rate limits for your use case
- [ ] Set appropriate `MAX_CONTENT_LENGTH`
- [ ] Enable HTTPS in production
- [ ] Set up proper logging/monitoring

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
tail -f app.log

# Search for errors
grep ERROR app.log

# Check performance
grep "elapsed" app.log
```

### Check Cache Performance
Logs show cache hits:
```
INFO - Using cached description (cache size: 23)
```

### Monitor Rate Limits
Check logs for rate limit violations:
```
WARNING - Rate limit exceeded
```

---

## 🎯 Testing the Application

### 1. Upload Test Image
- Visit http://127.0.0.1:5000
- Upload any image (jpg, png, gif, webp)
- Click "Get Song Recommendations"

### 2. Test Filters
- Select language (e.g., "English", "Hindi")
- Select artist
- Upload image again

### 3. Test Caching
- Upload the same image twice
- Second request should be instant (check logs)

### 4. Test Custom Song Generation
- After getting recommendations
- Click "Generate Song from This Description"
- Select mood and genre
- Wait for Suno.ai login (first time only)

---

## 🔄 Updating

### Pull Latest Changes
```bash
git pull origin main
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Rerun Setup
```bash
python setup.py
```

---

## 💡 Tips

1. **First startup is slow** (5-10s) due to model loading - this is normal
2. **Cache improves performance** - duplicate images return instantly
3. **Rate limiting** prevents abuse - adjust if needed for your use case
4. **Logs are your friend** - check `app.log` for debugging
5. **Suno.ai login** is required only once - session is saved

---

## 🆘 Getting Help

- Check [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed changes
- Check [RESUME_DESCRIPTIONS.md](RESUME_DESCRIPTIONS.md) for project talking points
- Open an issue on GitHub
- Check application logs: `tail -f app.log`

---

## 🎉 Success Indicators

Your setup is successful when:

✅ Application starts without errors
✅ Models load at startup (check logs)
✅ Upload endpoint returns recommendations
✅ Rate limiting is active
✅ Caching works (check logs on duplicate uploads)
✅ Logs are being written to `app.log`

---

**Ready to use!** 🚀
