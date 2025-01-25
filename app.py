import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS
from deep_translator import GoogleTranslator
import tempfile
import os

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyCC8Me5ZHBVBEuI3OZkoSZUF9sykvETxa8"
genai.configure(api_key=GOOGLE_API_KEY)

class StoryGenerator:
    def __init__(self):  # Corrected from _init_ to __init__
        # Use the correct model for vision tasks
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.language_map = {
            "telugu": "te",
            "hindi": "hi",
            "tamil": "ta",
            "kannada": "kn",
            "malayalam": "ml"
        }

    def generate_caption_and_story(self, image):
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            prompt = """
            1. First, describe what you see in this image in one sentence.
            2. Then, create an engaging children's story (200-300 words) based on what you see.
            Make the story suitable for ages 5-12, using simple language and a clear narrative.
            
            Format your response as:
            Caption: [your one-sentence description]
            
            Story: [your story]
            """

            # Create image part for the model
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_byte_arr
            }

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
            image = Image.open(image_file)
            st.image(image, caption='Uploaded Image', use_container_width=True)  # Updated parameter

            with st.spinner('Generating caption and story...'):
                caption, story = self.generate_caption_and_story(image)
                
                if caption:
                    st.write("### Generated Caption")
                    st.write(caption)
                
                if story:
                    st.write("### Story in English")
                    st.write(story)

                    with st.spinner('Generating English audio...'):
                        english_audio = self.text_to_speech(story, 'en')
                        if english_audio:
                            st.write("### English Audio")
                            st.audio(english_audio)

            if language_choice and language_choice.lower() in self.language_map:
                target_language = self.language_map[language_choice.lower()]
                
                with st.spinner(f'Translating to {language_choice}...'):
                    translated_text = self.translate_text(story, target_language)
                    
                    if translated_text:
                        st.write(f"### Story in {language_choice}")
                        st.write(translated_text)
                        
                        with st.spinner(f'Generating {language_choice} audio...'):
                            translated_audio = self.text_to_speech(translated_text, target_language)
                            if translated_audio:
                                st.write(f"### {language_choice} Audio")
                                st.audio(translated_audio)

            return caption, story

        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None, None

def main():
    st.set_page_config(
        page_title="Image Story Generator",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Image Story Generator")
    st.write("Upload an image to generate a story in multiple languages!")

    generator = StoryGenerator()

    col1, col2 = st.columns([2, 1])
    
    with col1:
        image_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
    
    with col2:
        language_choice = st.selectbox(
            "Select language for translation",
            ["None"] + list(generator.language_map.keys())
        )

    if image_file is not None:
        if st.button("Generate Story", type="primary"):
            if language_choice == "None":
                language_choice = None
                
            generator.process_image(image_file, language_choice)

            # Cleanup temporary files
            for file in os.listdir():
                if file.endswith('.mp3'):
                    try:
                        os.remove(file)
                    except:
                        pass

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ using Streamlit and Gemini AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":  # Corrected from _name_ to __name__
    main()
