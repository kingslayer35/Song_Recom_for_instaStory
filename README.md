# Image Song Recommender
<p align='center'>
<img src="static/uploads/Screenshot 2025-07-04 at 8.02.00 PM.png" width="450" height="330" >
</p>

**A beautiful UI for recommending songs based on an uploaded image, and generating new ones.**

## Overview

Image Song Recommender is an innovative Flask-based web application that offers personalized music experiences. It recommends existing songs and can even create new ones, all based on the mood and aesthetics extracted from an uploaded image. The app leverages state-of-the-art AI models like BLIP for initial image captioning and Google Gemini for refining descriptions and generating lyrics. For recommendations, it compares the refined image description against a precomputed song dataset, ranking songs by semantic similarity. The application also integrates Suno.ai for custom audio generation and provides interactive filters for users to refine recommendations by language and artist.

## ✨ Features

* **Intelligent Image Description:** Upload an image and automatically generate a detailed description using a combination of BLIP for initial captioning and Google Gemini for deep contextual analysis and emotional understanding. An option to provide an additional manual description allows for more tailored results.
* **Personalized Song Recommendations:** Receive a list of top song recommendations from a precomputed dataset, ranked by their semantic similarity to your image's description.
* **Filtering Options:** Refine song recommendations by selecting specific languages and artists.
* **Custom Song Generation:** Generate unique song lyrics (powered by Google Gemini) and corresponding audio (powered by Suno.ai) based on the image's description, with options to specify mood and genre.
* **Dynamic Web Interface:** A modern, user-friendly Flask-based web interface with a responsive design, background gradients, interactive filters, animated loading spinners, and clear error messages and feedback.

## 📁 Project Structure
image-song-recommender/
├── static/
│   ├── audio/                  # Stores dynamically generated audio files
│   └── uploads/                # Directory where uploaded images might temporarily be stored (e.g., for screenshot in README)
├── templates/
│   └── index.html              # Main HTML page for the web application's frontend.
├── app.py                      # Main Flask backend logic; processes image uploads, handles song recommendations and generation requests.
├── description.py              # Contains functions for image processing (BLIP, Gemini), description refinement, and song ranking (Sentence Transformers).
├── model.ipynb                 # Jupyter notebook for initial data processing, generating song embeddings, and model exploration.
├── README.md                   # Project README file (You are here!)
├── requirements.txt            # List of required Python packages for the project.
├── song_data.csv               # Raw song metadata (e.g., artist, track, description) used for precomputation.
├── song_data.pkl               # Precomputed song data (embeddings and metadata) for fast lookup in recommendations.
├── suno_automation.py          # Script for automating the Suno.ai login process and saving session cookies using Playwright.
└── suno_session_manager.py     # Manages the automated Suno.ai song generation process, including interacting with the Suno.ai interface.

## 🛠 Technologies Used

* **Backend:** Flask
* **Image Processing:** BLIP (Salesforce/blip-image-captioning-base)
* **Generative AI:** Google Gemini API (for description refinement and lyrics generation)
* **Song Recommendation:** Sentence Transformers (`all-mpnet-base-v2`) and Cosine Similarity
* **Audio Generation:** Suno.ai (automated via Playwright)
* **Browser Automation:** Playwright (for Suno.ai interactions)
* **Data Handling:** Pickle, Pandas
* **Frontend:** HTML, CSS, JavaScript

## 🚀 Setup and Installation

Follow these steps to get the project up and running on your local machine:

1.  **Clone the Repository**

    ```bash
    git clone [https://github.com/ish4722/Song_Recom_for_instaStory.git](https://github.com/ish4722/Song_Recom_for_instaStory.git)
    cd Song_Recom_for_instaStory
    ```

2.  **Create a Virtual Environment and Activate It (Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate   # On macOS/Linux
    # For Windows:
    # venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    *Note: After installing `playwright`, you might need to run `playwright install` to download necessary browser binaries.*

4.  **Google Gemini API Key**
    * Obtain your own Google Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    * **Important:** The API key is currently hardcoded in `app.py` and `description.py`. For security, **replace the placeholder key (`'AIzaSyC2KQPEjT-RDGoQwFJW2pgryK7gjr_ueqo'`) with your actual API key** in both files.

        ```python
        # Example change in app.py and description.py
        GEMINI_API_KEY = 'YOUR_ACTUAL_GEMINI_API_KEY_HERE'
        ```

5.  **Precompute Song Data**
    * Ensure that the `song_data.pkl` file is present in your project's root directory. This file contains the precomputed embeddings and metadata of your song dataset, which are crucial for fast recommendations.
    * If this file is missing or you need to update it (e.g., after modifying `song_data.csv`), you should run the relevant sections of the `model.ipynb` Jupyter notebook to generate it.

6.  **Suno.ai Login Automation**
    * The first time you attempt to generate a song using Suno.ai via this application, or if your session expires, the application will automatically launch a browser window (controlled by Playwright) to log into Suno.ai.
    * **Manual Intervention Required:** You **must** manually complete the Google login process and any visual security checks (e.g., CAPTCHA) that appear within this Playwright-controlled browser window. **It is critical not to close this window** until the login is successfully completed and the session is saved (a confirmation message will appear in your console, and the browser window will close automatically). A successful login will save your session to `suno_session.json` for future use.

## 🏃‍♀️ Usage

1.  **Run the Flask Application**

    ```bash
    python app.py
    ```

    By default, the application will run in debug mode and be accessible at `http://127.0.0.1:5000/`.

2.  **Access the Web Interface**
    Open your web browser and navigate to `http://127.0.0.1:5000/`.

3.  **Upload an Image**
    * On the homepage, click on the file input area (or drag and drop an image file) to upload your photo.
    * Optionally, type in a "Manual Description" to provide additional context or guidance for the AI.
    * Use the checkboxes to select preferred "Languages" and "Artists" to filter the song recommendations.
    * Click the "Get Song Recommendations" button. An animated spinner will indicate that the processing is underway.

4.  **View Results**
    * Once processed, a refined, detailed description of your uploaded image will be displayed.
    * Below the description, you will find a list of top song recommendations (including artist and track). You can expand each recommendation to view its similarity score and a detailed explanation of why it was recommended.

5.  **Generate a Custom Song**
    * Click the "Generate Song from This Description" button.
    * The application will first generate song lyrics using Google Gemini, and then attempt to create an audio track using Suno.ai.
    * **Important:** During the Suno.ai audio generation phase, a Playwright-controlled browser window will open. You might be prompted to complete a security check (e.g., a CAPTCHA). **Do not close this window manually.** Keep it open until the song generation is complete and the audio file has been downloaded or a link is provided.
    * Upon successful generation, the generated lyrics and an integrated audio player will appear on the page, allowing you to listen to and download your unique custom song.

## 🔮 Future Improvements

* **Enhanced Responsive and Mobile Design:** Further optimizations to ensure a flawless user experience across all device sizes.
* **User Accounts & History:** Implement user authentication to allow saving preferences, generated songs, and recommendation history.
* **Audio Previews:** Integrate with a music streaming API (e.g., Spotify API) to provide short audio previews for recommended tracks directly within the app.
* **Extended Filtering Options:** Introduce more advanced filtering criteria such as genre, specific moods, or release year for recommendations.
* **Robust Error Handling:** Improve error handling and provide more specific and user-friendly feedback for API failures, network issues, or other unexpected problems.

## 🙏 Acknowledgments

* **BLIP:** For powerful image captioning capabilities.
* **Google Gemini:** For its generative AI capabilities, enabling detailed description refinement and creative lyrics generation.
* **Suno.ai:** For providing an incredible AI-powered platform for music generation.
* **Sentence Transformers:** For efficient and accurate semantic embedding and similarity ranking.
* **Playwright:** For enabling robust browser automation necessary for interacting with Suno.ai.