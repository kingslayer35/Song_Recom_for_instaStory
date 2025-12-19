from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global model variables (initialized once)
st_model = None
blip_processor = None
blip_model = None

def init_models():
    """Initialize all AI models once at startup"""
    global st_model, blip_processor, blip_model

    if st_model is None:
        logger.info("Loading Sentence Transformer model...")
        st_model = SentenceTransformer('all-mpnet-base-v2')
        logger.info("Sentence Transformer loaded")

    if blip_processor is None or blip_model is None:
        logger.info("Loading BLIP model...")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        logger.info("BLIP model loaded")

def get_image_embedding(image_description):
    """Generate embedding for image description using Sentence Transformer"""
    if st_model is None:
        raise RuntimeError("Models not initialized. Call init_models() first.")
    return st_model.encode(image_description)

def rank_songs(image_description, precomputed_song_data, top_n=5):
    """
    Computes the embedding for the image description and compares it with precomputed song embeddings.
    Returns the top_n song recommendations as a list of tuples: (song_dict, similarity_score).
    """
    if st_model is None:
        raise RuntimeError("Models not initialized. Call init_models() first.")

    logger.info(f"Ranking songs for description: {image_description[:100]}...")

    image_embedding = get_image_embedding(image_description)
    similarities = []

    for song in precomputed_song_data:
        song_embedding = song['embedding']
        sim = cosine_similarity([image_embedding], [song_embedding])[0][0]
        similarities.append((song, sim))

    ranked = sorted(similarities, key=lambda x: x[1], reverse=True)
    logger.info(f"Ranked {len(similarities)} songs, returning top {top_n}")

    return ranked[:top_n]

def process_image(image_file, manual_description=None):
    """
    Processes an uploaded image file:
      1. Uses the BLIP model to generate an initial caption.
      2. If provided, appends a manual description.
      3. Uses Google Gemini to refine the combined description.
    Returns the refined description.
    """
    if blip_processor is None or blip_model is None:
        raise RuntimeError("Models not initialized. Call init_models() first.")

    # Get Gemini API key from environment
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY not configured. Please set it in your .env file")

    genai.configure(api_key=GEMINI_API_KEY)

    try:
        # Open image and convert to RGB
        logger.info("Processing image with BLIP...")
        image = Image.open(image_file).convert('RGB')

        # Generate initial caption using BLIP (using pre-loaded models)
        inputs = blip_processor(image, return_tensors="pt")
        out = blip_model.generate(**inputs)
        initial_caption = blip_processor.decode(out[0], skip_special_tokens=True)
        logger.info(f"BLIP caption: {initial_caption}")

        # Combine BLIP caption with the manual description if provided
        if manual_description:
            combined_prompt = f"Description: {initial_caption}. Additional details: {manual_description}"
            logger.info(f"Combined with manual description: {manual_description}")
        else:
            combined_prompt = f"Description: {initial_caption}"

        # Refine the combined description using Google Gemini
        logger.info("Refining description with Gemini...")
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are an expert in analyzing visual content and emotions. Given the description of an image, "
                "provide a single, detailed, and expressive description that captures the overall mood, background, "
                "and key visual elements (such as gestures, facial expressions, and environment). "
                "The response should be unified and vivid, description should be in very detail"
            )
        )

        response = gemini_model.generate_content([combined_prompt])
        refined_description = None

        try:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if isinstance(candidate.content, str):
                    refined_description = candidate.content
                elif hasattr(candidate.content, 'parts'):
                    refined_description = candidate.content.parts[0].text
                else:
                    refined_description = str(candidate.content)
        except Exception as e:
            logger.warning(f"Gemini refinement failed, using BLIP caption: {e}")
            refined_description = initial_caption  # fallback if Gemini fails

        logger.info(f"Final refined description: {refined_description[:100]}...")
        return refined_description

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise
