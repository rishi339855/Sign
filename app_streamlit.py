import streamlit as st
import subprocess
import sys
import os
import pymongo
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
import time
import io
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# --- App Logo + Title Header ---
st.set_page_config(
    page_title="SignBridge AI",
    page_icon="🧏‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Fun confetti on load
rain(
    emoji="👐",
    font_size=54,
    falling_speed=5,
    animation_length="infinite"
)

st.markdown("""
<style>
    .main {background-color: #f8f9fa !important;}
    .stButton>button {font-size: 1.1em; border-radius: 1.5em; padding: 0.6em 2em;}
    .stTextInput>div>div>input {font-size: 1.1em; border-radius: 1em;}
    .stDownloadButton>button {font-size: 1.1em; border-radius: 1.5em;}
    .navbar {
        display: flex;
        justify-content: center;
        align-items: center;
        background: linear-gradient(90deg,#7b2ff2,#f357a8);
        border-radius: 2em;
        margin-bottom: 2em;
        padding: 0.5em 0;
        box-shadow: 0 4px 16px #f357a880;
    }
    .navbar-btn {
        color: white;
        background: none;
        border: none;
        font-size: 1.1em;
        margin: 0 1.5em;
        padding: 0.5em 1.5em;
        border-radius: 1.5em;
        cursor: pointer;
        transition: background 0.2s;
    }
    .navbar-btn.selected, .navbar-btn:hover {
        background: rgba(255,255,255,0.18);
        font-weight: bold;
    }
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5em;
    }
    .app-logo {
        font-size: 2.5em;
        margin-right: 0.5em;
    }
    .app-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #7b2ff2;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(
    """
    <div class="app-header">
        <span class="app-logo">🧏‍♂️</span>
        <span class="app-title">SignBridge AI</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Navbar (Streamlit-native) ---
nav_options = ["Home", "ASL to Text", "Text/Voice to Sign", "AI Assistant"]
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = nav_options[0]
nav_page = st.radio(
    "Navigation",
    nav_options,
    index=nav_options.index(st.session_state["nav_page"]),
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state["nav_page"] = nav_page

# --- Page Routing ---
page = st.session_state["nav_page"]

if page == "Home":
    colored_header(
        label="Welcome to SignBridge AI",
        description="Bridging communication with AI-powered sign language detection, grammar correction, and speech.",
        color_name="violet-70"
    )
    st.markdown("""
    <div style='text-align:center; font-size:1.2em; margin-top:2em;'>
        <b>Choose a feature from the navigation bar above to get started!</b>
    </div>
    """, unsafe_allow_html=True)

elif page == "ASL to Text":
    # --- ASL to Text Section (current main logic) ---
    from deep_translator import GoogleTranslator
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
    mongo_db = mongo_client['SIGN']
    mongo_collection = mongo_db['sentences']
    load_dotenv()
    
    # Language selection (English default, scrollable)
    lang_dict = {
        'English': 'en',
        'Arabic': 'ar',
        'Bengali': 'bn',
        'Chinese (Simplified)': 'zh-cn',
        'French': 'fr',
        'German': 'de',
        'Gujarati': 'gu',
        'Hindi': 'hi',
        'Japanese': 'ja',
        'Kannada': 'kn',
        'Malayalam': 'ml',
        'Marathi': 'mr',
        'Punjabi': 'pa',
        'Russian': 'ru',
        'Spanish': 'es',
        'Tamil': 'ta',
        'Telugu': 'te',
        'Urdu': 'ur',
    }
    lang_keys = ['English'] + sorted([k for k in lang_dict if k != 'English'])
    lang_choice = st.selectbox("Select language for translation:", lang_keys, index=0)
    target_lang = lang_dict[lang_choice]
    
    if st.button("Launch Sign Language Detection", help="Open the sign language detection window."):
        python_executable = sys.executable  # Path to the current Python interpreter
        script_path = os.path.join(os.getcwd(), "final_pred.py")
        os.system(f'start "" "{python_executable}" "{script_path}"')
        st.success("Sign language detection started! Please check for a new window.")
    
    st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)
    colored_header(
        label="Recent Message",
        description="Latest detected sentence, with options to speak, refresh, or correct.",
        color_name="blue-70"
    )
    col1, col2, col3, col4 = st.columns([5, 1, 1, 3])
    with col1:
        sentence_doc = mongo_collection.find_one({'_id': 'current'})
        if sentence_doc and 'sentence' in sentence_doc:
            recent_sentence = sentence_doc['sentence']
            st.markdown(f"<div style='font-size:1.2em;color:#7b2ff2;font-weight:bold;'>{recent_sentence}</div>", unsafe_allow_html=True)
            # Translate the sentence
            if recent_sentence.strip():
                try:
                    translated_text = GoogleTranslator(source='auto', target=target_lang).translate(recent_sentence)
                    st.markdown(f"<div style='font-size:1.1em;color:#43b97f;'><b>Translated ({lang_choice}):</b> {translated_text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Translation error: {e}")
        else:
            recent_sentence = ""
            st.write("No message yet.")
    with col2:
        if st.button("🔊", help="Speak the recent message"):
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(recent_sentence)
                engine.runAndWait()
            except RuntimeError as e:
                if "run loop already started" in str(e):
                    st.warning("Text-to-speech is already running. Please wait a moment.")
                else:
                    st.error(f"Text-to-speech error: {e}")
    with col3:
        if st.button("🔄", help="Refresh the recent message"):
            st.rerun()
    with col4:
        st.markdown("<span style='color:#f357a8;font-weight:bold;'>LLM Model:</span> Llama-3", unsafe_allow_html=True)
        if st.button("✨ Correct Grammar & Spelling", help="Use Groq LLM and SpellChecker"):
            if recent_sentence.strip():
                if ' ' not in recent_sentence.strip():
                    from spellchecker import SpellChecker
                    spell = SpellChecker()
                    correction = spell.correction(recent_sentence)
                    st.info(f"SpellChecker correction: {correction}")
                    groq_api_key = os.getenv("GROQ_API_KEY")
                    if not groq_api_key:
                        st.warning("Groq API key not found. Please set GROQ_API_KEY in your environment or .env file.")
                    else:
                        import openai
                        client = openai.OpenAI(
                            api_key=groq_api_key,
                            base_url="https://api.groq.com/openai/v1"
                        )
                        prompt = (
                            "Correct the following text for both spelling and grammar. "
                            "Only return the corrected text, nothing else.\n\n"
                            f"Text: {recent_sentence}"
                        )
                        with st.spinner("Contacting Groq API for correction..."):
                            try:
                                response = client.chat.completions.create(
                                    model="llama3-70b-8192",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful assistant that corrects spelling and grammar."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    max_tokens=128,
                                    temperature=0.2
                                )
                                corrected_llm = response.choices[0].message.content.strip()
                                st.success(f"Groq LLM correction: {corrected_llm}")
                            except Exception as e:
                                st.error(f"Groq API error: {e}")
                else:
                    import openai
                    groq_api_key = os.getenv("GROQ_API_KEY")
                    if not groq_api_key:
                        st.warning("Groq API key not found. Please set GROQ_API_KEY in your environment or .env file.")
                    else:
                        client = openai.OpenAI(
                            api_key=groq_api_key,
                            base_url="https://api.groq.com/openai/v1"
                        )
                        prompt = (
                            "Correct the following text for both spelling and grammar. "
                            "Only return the corrected text, nothing else.\n\n"
                            f"Text: {recent_sentence}"
                        )
                        with st.spinner("Contacting Groq API for correction..."):
                            try:
                                response = client.chat.completions.create(
                                    model="llama3-70b-8192",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful assistant that corrects spelling and grammar."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    max_tokens=128,
                                    temperature=0.2
                                )
                                corrected = response.choices[0].message.content.strip()
                                st.success(f"Groq LLM correction: {corrected}")
                            except Exception as e:
                                st.error(f"Groq API error: {e}")

elif page == "Text/Voice to Sign":
    # --- Text/Voice to Sign Section (video generation) ---
    colored_header(
        label="Text to Sign Language Video",
        description="Enter any text and get a video showing the sign language sequence for your text!",
        color_name="green-70"
    )
    st.markdown("""
    <div style='background: #eaf6f6; border-radius: 1.5em; padding: 2em 2em 1em 2em; margin-bottom: 2em;'>
        <div style='font-size:1.2em; color:#222; margin-bottom:1em;'>🎬 <b>Generate a Sign Language Video</b></div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for video text
    if "video_text" not in st.session_state:
        st.session_state["video_text"] = ""
    
    # Input method selection
    st.markdown("### Choose Input Method:")
    
    # Method 1: Typed Text
    st.markdown("**1. Type Text:**")
    typed_text = st.text_input("Enter text to generate sign language video:", key="video_text_input")
    if typed_text.strip():
        st.session_state["video_text"] = typed_text
    
    # Method 2: Recently Detected Word
    st.markdown("**2. Use Recently Detected Word:**")
    # Fetch latest detected sentence from MongoDB
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
    mongo_db = mongo_client['SIGN']
    mongo_collection = mongo_db['sentences']
    sentence_doc = mongo_collection.find_one({'_id': 'current'})
    
    if sentence_doc and 'sentence' in sentence_doc and sentence_doc['sentence'].strip():
        recent_sentence = sentence_doc['sentence']
        # Extract the last word from the sentence
        words = recent_sentence.strip().split()
        last_word = words[-1] if words else ""
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Last detected word:** <span style='color:#7b2ff2;font-size:1.1em'>{last_word}</span>", unsafe_allow_html=True)
        with col2:
            if st.button("Use This Word", key="use_last_word_btn"):
                st.session_state["video_text"] = last_word
                st.success(f"Using word: {last_word}")
    else:
        st.info("No detected words available. Use ASL to Text feature first.")

    # Method 2.5: Select from History
    st.markdown("**2.5. Select from History:**")
    # Fetch recent history for selection
    history_docs = list(mongo_collection.find({'_id': {'$ne': 'current'}}).sort('timestamp', -1).limit(10))
    if history_docs:
        history_options = []
        for doc in history_docs:
            sentence = doc.get('sentence', '')
            timestamp = doc.get('timestamp', '')
            if hasattr(timestamp, 'strftime'):
                formatted_time = timestamp.strftime("%H:%M:%S")
            else:
                formatted_time = str(timestamp)
            history_options.append(f"{sentence} ({formatted_time})")
        selected_history = st.selectbox(
            "Choose from recent detections:",
            ["Select a sentence..."] + history_options,
            key="history_select"
        )
        if selected_history and selected_history != "Select a sentence...":
            selected_sentence = selected_history.split(" (")[0]
            if st.button("Use Selected Sentence", key="use_history_btn"):
                st.session_state["video_text"] = selected_sentence
                st.success(f"Using sentence: {selected_sentence}")
    else:
        st.info("No history available yet. Use ASL to Text feature to build history!")
    
    # Method 3: Voice Input
    st.markdown("**3. Voice Input:**")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Click the button below and speak your text:")
    with col2:
        if st.button("🎤 Record Voice", key="voice_record_btn"):
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                
                with st.spinner("Listening... Speak now!"):
                    with sr.Microphone() as source:
                        # Adjust for ambient noise
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                with st.spinner("Processing speech..."):
                    try:
                        voice_text = recognizer.recognize_google(audio)
                        st.session_state["video_text"] = voice_text
                        st.success(f"Voice input: {voice_text}")
                    except sr.UnknownValueError:
                        st.error("Could not understand the audio. Please try again.")
                    except sr.RequestError as e:
                        st.error(f"Could not request results; {e}")
            except ImportError:
                st.error("Speech recognition not available. Please install SpeechRecognition and pyaudio packages.")
                st.info("Run: pip install SpeechRecognition pyaudio")
            except Exception as e:
                st.error(f"Voice recording error: {e}")
                st.info("Please ensure microphone is connected and permissions are granted.")
    
    # Display current selected text
    if st.session_state["video_text"]:
        st.markdown("---")
        st.markdown(f"**Current text for video generation:** <span style='color:#43b97f;font-size:1.2em'>{st.session_state['video_text']}</span>", unsafe_allow_html=True)
    
    # Generate video section
    st.markdown("---")
    st.markdown("### Generate Video:")
    generate_col, download_col = st.columns([2, 2])
    with generate_col:
        if st.button("Generate Sign Language Video", key="generate_video_btn"):
            if st.session_state["video_text"].strip():
                with st.spinner("Generating video, please wait..."):
                    result = subprocess.run([
                        sys.executable, "text_to_sign_video.py", st.session_state["video_text"]
                    ], capture_output=True, text=True)
                    time.sleep(1)
                if os.path.exists("output_sign_sequence.mp4"):
                    with open("output_sign_sequence.mp4", "rb") as video_file:
                        video_bytes = video_file.read()
                    st.success("Video generated! You can download it below.")
                    with download_col:
                        st.download_button(
                            label="⬇️ Download Sign Language Video",
                            data=video_bytes,
                            file_name="sign_language_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Video could not be generated. Please try again.")
            else:
                st.info("Please select or enter some text to generate the video.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Real-Time Chat":
    colored_header(
        label="Real-Time Chat",
        description="Coming soon: Real-time chat with sign language translation!",
        color_name="orange-70"
    )
    st.info("This feature is coming soon!")

elif page == "AI Assistant":
    colored_header(
        label="AI Assistant",
        description="Ask any question using sign language! The AI will answer and you can view/download the response as a sign language video.",
        color_name="red-70"
    )
    st.markdown("""
    <div style='background: #f8eaf6; border-radius: 1.5em; padding: 2em 2em 1em 2em; margin-bottom: 2em;'>
        <div style='font-size:1.2em; color:#222; margin-bottom:1em;'>🤖 <b>Ask the AI Assistant</b></div>
    """, unsafe_allow_html=True)
    # Fetch latest detected sentence from MongoDB
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
    mongo_db = mongo_client['SIGN']
    mongo_collection = mongo_db['sentences']
    sentence_doc = mongo_collection.find_one({'_id': 'current'})
    if sentence_doc and 'sentence' in sentence_doc and sentence_doc['sentence'].strip():
        detected_question = sentence_doc['sentence']
        st.markdown(f"<b>Detected Question:</b> <span style='color:#7b2ff2;font-size:1.2em'>{detected_question}</span>", unsafe_allow_html=True)
        ask_ai_disabled = False
    else:
        st.info("No question detected yet. Please use the ASL to Text feature to generate your question.")
        detected_question = ""
        ask_ai_disabled = True
    if "ai_answer" not in st.session_state:
        st.session_state["ai_answer"] = ""
    if st.button("Ask AI", key="ask_ai_btn", disabled=ask_ai_disabled):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            st.warning("Groq API key not found. Please set GROQ_API_KEY in your environment or .env file.")
        else:
            import openai
            client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            # Improved prompt for simple, max 3-word answers
            prompt = (
                "Answer the following question as simply as possible, using a maximum of 3 words. "
                "If the question cannot be answered simply, respond with 'Cannot answer'.\n\n"
                f"Question: {detected_question}"
            )
            with st.spinner("AI is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant for the deaf and hard of hearing. Always answer as simply as possible, using a maximum of 3 words. If the question cannot be answered simply, respond with 'Cannot answer'."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=20,
                        temperature=0.2
                    )
                    ai_answer = response.choices[0].message.content.strip()
                    st.session_state["ai_answer"] = ai_answer
                    st.success(f"AI Response: {ai_answer}")
                    # Generate sign language video for the response
                    with st.spinner("Generating sign language video for the response..."):
                        result = subprocess.run([
                            sys.executable, "text_to_sign_video.py", ai_answer
                        ], capture_output=True, text=True)
                        time.sleep(1)
                    if os.path.exists("output_sign_sequence.mp4"):
                        with open("output_sign_sequence.mp4", "rb") as video_file:
                            video_bytes = video_file.read()
                        st.success("Sign language video generated! You can download it below.")
                        st.download_button(
                            label="⬇️ Download AI Response as Sign Language Video",
                            data=video_bytes,
                            file_name="ai_response_sign_language_video.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error("Video could not be generated. Please try again.")
                except Exception as e:
                    st.error(f"Groq API error: {e}")
    # Speak AI Response button (works after rerun)
    ai_answer = st.session_state.get("ai_answer", "")
    if ai_answer and ai_answer.lower() != "cannot answer":
        if st.button("🔊 Speak AI Response", key="speak_ai_response"):
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(ai_answer)
                engine.runAndWait()
            except RuntimeError as e:
                if "run loop already started" in str(e):
                    st.warning("Text-to-speech is already running. Please wait a moment.")
                else:
                    st.error(f"Text-to-speech error: {e}")
            except Exception as e:
                st.error(f"Text-to-speech error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)




