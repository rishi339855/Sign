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

# Set page config for better look
st.set_page_config(
    page_title="Sign Language to Text & Speech",
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

# Beautiful header
colored_header(
    label="Sign Language to Text & Speech",
    description="Bridging communication with AI-powered sign language detection, grammar correction, and speech.",
    color_name="violet-70"
)

st.markdown("""
<style>
    .main {background-color: #f8f9fa !important;}
    .stButton>button {font-size: 1.1em; border-radius: 1.5em; padding: 0.6em 2em;}
    .stTextInput>div>div>input {font-size: 1.1em; border-radius: 1em;}
    .stDownloadButton>button {font-size: 1.1em; border-radius: 1.5em;}
</style>
""", unsafe_allow_html=True)

# MongoDB setup
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
mongo_db = mongo_client['SIGN']
mongo_collection = mongo_db['sentences']

# Load environment variables
load_dotenv()

# --- Section 1: Communicate with People ---
st.markdown("""
<div style='text-align:center; margin-bottom: 2em;'>
    <button style='background:linear-gradient(90deg,#7b2ff2,#f357a8);color:white;padding:1em 2em;border:none;border-radius:2em;font-size:1.3em;box-shadow:0 4px 16px #f357a880;cursor:pointer;' onclick="window.open('','_blank');">🧏‍♂️ Communicate with people</button>
</div>
""", unsafe_allow_html=True)
if st.button("Launch Sign Language Detection", help="Open the sign language detection window."):
    python_executable = sys.executable  # Path to the current Python interpreter
    script_path = os.path.join(os.getcwd(), "final_pred.py")
    os.system(f'start "" "{python_executable}" "{script_path}"')
    st.success("Sign language detection started! Please check for a new window.")

st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)

# --- Section 2: Recent Message ---
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
    else:
        recent_sentence = ""
        st.write("No message yet.")
with col2:
    if st.button("🔊", help="Speak the recent message"):
        import pyttsx3
        import threading
        def speak_text(text):
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        if recent_sentence.strip():
            threading.Thread(target=speak_text, args=(recent_sentence,), daemon=True).start()
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
        else:
            st.info("No message to correct.")

st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)

# --- Section 3: Text to Sign Language Video ---
colored_header(
    label="Text to Sign Language Video",
    description="Enter any text and get a video showing the sign language sequence for your text!",
    color_name="green-70"
)
st.markdown("""
<div style='background: #eaf6f6; border-radius: 1.5em; padding: 2em 2em 1em 2em; margin-bottom: 2em;'>
    <div style='font-size:1.2em; color:#222; margin-bottom:1em;'>🎬 <b>Generate a Sign Language Video</b></div>
""", unsafe_allow_html=True)

video_text = st.text_input("Enter text to generate sign language video:", key="video_text_input")
generate_col, download_col = st.columns([2, 2])
with generate_col:
    if st.button("Generate Sign Language Video", key="generate_video_btn"):
        if video_text.strip():
            with st.spinner("Generating video, please wait..."):
                result = subprocess.run([
                    sys.executable, "text_to_sign_video.py", video_text
                ], capture_output=True, text=True)
                time.sleep(1)
            if os.path.exists("output_sign_sequence.mp4"):
                with open("output_sign_sequence.mp4", "rb") as video_file:
                    video_bytes = video_file.read()
                st.video(io.BytesIO(video_bytes))
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
            st.info("Please enter some text to generate the video.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)

# --- Section 4: Tips ---
st.markdown("""
<div style='text-align:center;color:#888;font-size:1.1em; margin-top:2em;'>
    <b>Tip:</b> Use the <span style='color:#f357a8;'>Communicate with people</span> button to launch sign language detection.<br>
    The <span style='color:#7b2ff2;'>Recent Message</span> section shows the latest detected sentence.<br>
    Use <b>🔊</b> to speak, <b>🔄</b> to refresh, and <b>✨</b> to correct grammar and spelling.<br>
    Try the <span style='color:#43b97f;'>Text to Sign Language Video</span> feature to visualize any phrase in sign language!<br>
</div>
""", unsafe_allow_html=True)




