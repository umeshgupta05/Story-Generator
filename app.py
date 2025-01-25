import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS
from deep_translator import GoogleTranslator
import tempfile
import os
import time

# Configure page
st.set_page_config(
    page_title="✨ Magic Story Generator ✨",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .story-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        animation: fadeIn 0.5s ease-in;
    }
    .caption-text {
        font-size: 1.2rem;
        color: #333;
        font-style: italic;
        margin-bottom: 1rem;
    }
    .language-selector {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .header-text {
        background: linear-gradient(45deg, #ff4b4b, #ff9b9b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in;
    }
    .subheader {
        color: #666;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in;
    }
    .upload-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .stAudio {
        margin-top: 1rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .spinner {
        text-align: center;
        padding: 2rem;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        animation: fadeIn 2s ease-in;
    }
    </style>
    """, unsafe_allow_html=True)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyCC8Me5ZHBVBEuI3OZkoSZUF9sykvETxa8"  # Replace with your API key
genai.configure(api_key=GOOGLE_API_KEY)

class EnhancedStoryGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.language_map = {
            "Telugu": "te",
            "Hindi": "hi",
            "Tamil": "ta",
            "Kannada": "kn",
            "Malayalam": "ml"
        }

    def generate_caption_and_story(self, image):
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            image_part = {
                "mime_type": "image/jpeg",
                "data": img_byte_arr
            }

            prompt = """
            1. First, describe what you see in this image in one sentence.
            2. Then, create an engaging children's story (200-300 words) based on what you see.
            Make the story suitable for ages 5-12, using simple language and a clear narrative.
            
            Format your response as:
            Caption: [your one-sentence description]
            
            Story: [your story]
            """

            response = self.model.generate_content([prompt, image_part])
            response_text = response.text

            try:
                caption_part = response_text.split("Caption:")[1].split("Story:")[0].strip()
                story_part = response_text.split("Story:")[1].strip()
                return caption_part, story_part
            except:
                st.error("Error parsing the response. Using full response as story.")
                return "Image description", response_text

        except Exception as e:
            st.error(f"Error generating content: {str(e)}")
            return None, None

    def translate_text(self, text, target_language):
        if not text:
            return None
            
        try:
            translator = GoogleTranslator(source='en', target=target_language)
            max_chunk_size = 4500
            chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return ' '.join(translated_chunks)
        except Exception as e:
            st.error(f"Error translating text: {str(e)}")
            return None

    def text_to_speech(self, text, language_code):
        if not text:
            return None
            
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts = gTTS(text=text, lang=language_code)
                tts.save(tmp_file.name)
                return tmp_file.name
        except Exception as e:
            st.error(f"Error generating speech: {str(e)}")
            return None

    def process_image(self, image_file, language_choice=None):
        try:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                image = Image.open(image_file)
                # Updated parameter from use_column_width to use_container_width
                st.image(image, caption='✨ Your Magical Image ✨', use_container_width=True)

            with col2:
                with st.spinner('🌟 Creating magic...'):
                    time.sleep(1)  # For effect
                    
                    with st.container():
                        st.markdown("<div class='story-container'>", unsafe_allow_html=True)
                        caption, story = self.generate_caption_and_story(image)
                        
                        if caption:
                            st.markdown(f"<p class='caption-text'>📝 {caption}</p>", unsafe_allow_html=True)
                        
                        if story:
                            st.markdown("### 📖 Your Magical Story")
                            st.write(story)
                            
                            with st.expander("🎧 Listen to the Magic"):
                                english_audio = self.text_to_speech(story, 'en')
                                if english_audio:
                                    st.audio(english_audio)
                        st.markdown("</div>", unsafe_allow_html=True)

            if language_choice and language_choice != "None":
                with st.container():
                    st.markdown("<div class='story-container'>", unsafe_allow_html=True)
                    target_language = self.language_map[language_choice]
                    
                    with st.spinner(f'✨ Translating to {language_choice}...'):
                        translated_text = self.translate_text(story, target_language)
                        
                        if translated_text:
                            st.markdown(f"### 🌏 Story in {language_choice}")
                            st.write(translated_text)
                            
                            with st.expander(f"🎧 Listen in {language_choice}"):
                                translated_audio = self.text_to_speech(translated_text, target_language)
                                if translated_audio:
                                    st.audio(translated_audio)
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"✨ Oops! Magic failed: {str(e)}")
            return None, None

def main():
    st.markdown("<h1 class='header-text'>✨ Magic Story Generator ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Transform your images into enchanting stories!</p>", unsafe_allow_html=True)

    generator = EnhancedStoryGenerator()

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
        image_file = st.file_uploader("🖼️ Choose your magical image", type=['png', 'jpg', 'jpeg'])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='language-selector'>", unsafe_allow_html=True)
        language_choice = st.selectbox(
            "🌍 Choose your story's language",
            ["None"] + list(generator.language_map.keys())
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if image_file is not None:
        if st.button("✨ Generate Magical Story ✨", type="primary"):
            if language_choice == "None":
                language_choice = None
            
            with st.spinner('🪄 Casting the spell...'):
                generator.process_image(image_file, language_choice)

    st.markdown("---")
    st.markdown(
        """
        <div class='footer'>
            <p>✨ Crafted with magic using Streamlit and Gemini AI ✨</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
