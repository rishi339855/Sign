import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
from app_logic import SignLanguageLogic

# Initialize the logic class
logic = SignLanguageLogic()

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
    # --- ASL to Text Section ---
    colored_header(
        label="ASL to Text",
        description="Detect sign language and convert to text with translation and correction features.",
        color_name="blue-70"
    )
    
    # Language selection
    lang_keys = logic.get_language_keys()
    lang_choice = st.selectbox("Select language for translation:", lang_keys, index=0)
    target_lang = logic.lang_dict[lang_choice]
    
    # Launch detection button
    if st.button("Launch Sign Language Detection", help="Open the sign language detection window."):
        result = logic.launch_sign_detection()
        st.success(result)
    
    # Storage Control Section
    st.markdown("<hr style='border:1px solid #eee; margin:1em 0;'>", unsafe_allow_html=True)
    colored_header(
        label="Storage Control",
        description="Control when detected text gets stored in the database.",
        color_name="orange-70"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        storage_status = logic.get_storage_status()
        if storage_status:
            st.markdown("🟢 **Status:** Automatic storage enabled")
        else:
            st.markdown("🔴 **Status:** Automatic storage disabled")
    
    with col2:
        if st.button("🟢 Enable Auto Storage", key="enable_storage_btn"):
            result = logic.start_text_storage()
            st.success(result)
            st.rerun()
    
    with col3:
        if st.button("🔴 Disable Auto Storage", key="disable_storage_btn"):
            result = logic.stop_text_storage()
            st.success(result)
            st.rerun()
    
    # Manual storage section
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Manual Storage:** Store the current detected text in history")
    with col2:
        if st.button("💾 Store Current Text", key="store_current_btn"):
            result = logic.store_current_text()
            if result.startswith("Successfully stored"):
                st.success(result)
            else:
                st.info(result)
            st.rerun()
    
    st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)
    
    # Recent Message Section
    colored_header(
        label="Recent Message",
        description="Latest detected sentence, with options to speak, refresh, or correct.",
        color_name="blue-70"
    )
    
    col1, col2, col3, col4 = st.columns([5, 1, 1, 3])
    with col1:
        recent_sentence = logic.get_current_sentence()
        if recent_sentence:
            st.markdown(f"<div style='font-size:1.2em;color:#7b2ff2;font-weight:bold;'>{recent_sentence}</div>", unsafe_allow_html=True)
            # Translate the sentence
            translated_text = logic.translate_sentence(recent_sentence, target_lang)
            if translated_text and not translated_text.startswith("Translation error"):
                st.markdown(f"<div style='font-size:1.1em;color:#43b97f;'><b>Translated ({lang_choice}):</b> {translated_text}</div>", unsafe_allow_html=True)
            elif translated_text.startswith("Translation error"):
                st.warning(translated_text)
        else:
            st.write("No message yet.")
    
    with col2:
        if st.button("🔊", help="Speak the recent message"):
            result = logic.speak_text(recent_sentence)
            if result != True:
                st.warning(result)
    
    with col3:
        if st.button("🔄", help="Refresh the recent message"):
            st.rerun()
    
    with col4:
        st.markdown("<span style='color:#f357a8;font-weight:bold;'>LLM Model:</span> Llama-3", unsafe_allow_html=True)
        if st.button("✨ Correct Grammar & Spelling", help="Use Groq LLM and SpellChecker"):
            if recent_sentence.strip():
                with st.spinner("Correcting text..."):
                    result = logic.correct_grammar_spelling(recent_sentence)
                    if result.startswith("SpellChecker correction:"):
                        st.info(result)
                    elif result.startswith("Groq LLM correction:"):
                        st.success(result)
                    elif result.startswith("Groq API key not found"):
                        st.warning(result)
                    elif result.startswith("Groq API error"):
                        st.error(result)
                    else:
                        st.info(result)
            else:
                st.info("No message to correct.")
    
    # --- History Section ---
    st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)
    colored_header(
        label="Detection History",
        description="All detected sentences with at least 2 letters, stored with timestamps.",
        color_name="violet-70"
    )
    
    # Add clear all history button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Recent Detections:**")
    with col2:
        if st.button("🗑️ Clear All History", key="clear_all_history_btn", type="secondary"):
            result = logic.clear_all_history()
            st.success(result)
            st.rerun()
    
    history_docs = logic.get_detection_history(20)
    if history_docs:
        for i, doc in enumerate(history_docs):
            timestamp = doc.get('timestamp', 'Unknown time')
            sentence = doc.get('sentence', '')
            word_count = doc.get('word_count', 0)
            char_count = doc.get('char_count', 0)
            formatted_time = logic.format_timestamp(timestamp)
            
            with st.expander(f"📝 {sentence} ({formatted_time})"):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**Text:** {sentence}")
                with col2:
                    st.markdown(f"**Words:** {word_count}")
                with col3:
                    st.markdown(f"**Chars:** {char_count}")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"🔊 Speak", key=f"speak_history_{i}"):
                        result = logic.speak_text(sentence)
                        if result != True:
                            st.error(result)
                
                with col2:
                    if st.button(f"📋 Copy", key=f"copy_history_{i}"):
                        st.write("Text copied to clipboard!")
                        st.code(sentence)
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_history_{i}"):
                        logic.delete_history_item(doc['_id'])
                        st.success("Deleted from history!")
                        st.rerun()
    else:
        st.info("No detection history yet. Start using sign language detection to build history!")
    
    st.markdown("<hr style='border:1px solid #eee; margin:2em 0;'>", unsafe_allow_html=True)

elif page == "Text/Voice to Sign":
    # --- Text/Voice to Sign Section ---
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
    recent_sentence = logic.get_current_sentence()
    
    if recent_sentence.strip():
        last_word = logic.get_last_word_from_sentence(recent_sentence)
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
    history_docs = logic.get_detection_history(10)
    
    if history_docs:
        history_options = []
        for doc in history_docs:
            sentence = doc.get('sentence', '')
            timestamp = doc.get('timestamp', '')
            formatted_time = logic.format_short_timestamp(timestamp)
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
            with st.spinner("Listening... Speak now!"):
                voice_text = logic.record_voice_input()
            
            if voice_text.startswith("Could not understand") or voice_text.startswith("Could not request") or voice_text.startswith("Speech recognition not available") or voice_text.startswith("Voice recording error"):
                st.error(voice_text)
            else:
                st.session_state["video_text"] = voice_text
                st.success(f"Voice input: {voice_text}")
    
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
                    result = logic.generate_sign_video(st.session_state["video_text"])
                
                if isinstance(result, bytes):
                    st.success("Video generated! You can download it below.")
                    with download_col:
                        st.download_button(
                            label="⬇️ Download Sign Language Video",
                            data=result,
                            file_name="sign_language_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(result)
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
    detected_question = logic.get_current_sentence()
    
    if detected_question.strip():
        st.markdown(f"<b>Detected Question:</b> <span style='color:#7b2ff2;font-size:1.2em'>{detected_question}</span>", unsafe_allow_html=True)
        ask_ai_disabled = False
    else:
        st.info("No question detected yet. Please use the ASL to Text feature to generate your question.")
        detected_question = ""
        ask_ai_disabled = True
    
    if "ai_answer" not in st.session_state:
        st.session_state["ai_answer"] = ""
    
    if st.button("Ask AI", key="ask_ai_btn", disabled=ask_ai_disabled):
        with st.spinner("AI is thinking..."):
            ai_answer = logic.ask_ai_assistant(detected_question)
            
            if ai_answer.startswith("Groq API key not found"):
                st.warning(ai_answer)
            elif ai_answer.startswith("Groq API error"):
                st.error(ai_answer)
            else:
                st.session_state["ai_answer"] = ai_answer
                st.success(f"AI Response: {ai_answer}")
                
                # Generate sign language video for the response
                with st.spinner("Generating sign language video for the response..."):
                    video_result = logic.generate_sign_video(ai_answer)
                
                if isinstance(video_result, bytes):
                    st.success("Sign language video generated! You can download it below.")
                    st.download_button(
                        label="⬇️ Download AI Response as Sign Language Video",
                        data=video_result,
                        file_name="ai_response_sign_language_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error(video_result)
    
    # Speak AI Response button (works after rerun)
    ai_answer = st.session_state.get("ai_answer", "")
    if ai_answer and ai_answer.lower() != "cannot answer":
        if st.button("🔊 Speak AI Response", key="speak_ai_response"):
            result = logic.speak_text(ai_answer)
            if result != True:
                st.error(result)
    
    st.markdown("</div>", unsafe_allow_html=True) 