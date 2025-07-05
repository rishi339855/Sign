import streamlit as st
import subprocess
import sys
import os
import pymongo
import time
import io
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()

class SignLanguageLogic:
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
        self.mongo_db = self.mongo_client['SIGN']
        self.mongo_collection = self.mongo_db['sentences']
        
        # Language dictionary for translation
        self.lang_dict = {
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
        
        # Control flag for storing text
        self.should_store_text = False
    
    def get_language_keys(self):
        """Get sorted language keys with English first"""
        return ['English'] + sorted([k for k in self.lang_dict if k != 'English'])
    
    def launch_sign_detection(self):
        """Launch the sign language detection window"""
        python_executable = sys.executable
        script_path = os.path.join(os.getcwd(), "final_pred.py")
        os.system(f'start "" "{python_executable}" "{script_path}"')
        return "Sign language detection started! Please check for a new window."
    
    def get_current_sentence(self):
        """Get the current detected sentence from MongoDB"""
        sentence_doc = self.mongo_collection.find_one({'_id': 'current'})
        if sentence_doc and 'sentence' in sentence_doc:
            return sentence_doc['sentence']
        return ""
    
    def translate_sentence(self, sentence, target_lang):
        """Translate a sentence to the target language"""
        if sentence.strip():
            try:
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(sentence)
                return translated_text
            except Exception as e:
                return f"Translation error: {e}"
        return ""
    
    def speak_text(self, text):
        """Convert text to speech"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
            return True
        except RuntimeError as e:
            if "run loop already started" in str(e):
                return "Text-to-speech is already running. Please wait a moment."
            else:
                return f"Text-to-speech error: {e}"
        except Exception as e:
            return f"Text-to-speech error: {e}"
    
    def correct_grammar_spelling(self, sentence):
        """Correct grammar and spelling using Groq LLM and SpellChecker"""
        if not sentence.strip():
            return "No message to correct."
        
        if ' ' not in sentence.strip():
            # Single word - use SpellChecker
            from spellchecker import SpellChecker
            spell = SpellChecker()
            correction = spell.correction(sentence)
            return f"SpellChecker correction: {correction}"
        else:
            # Multiple words - use Groq LLM
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                return "Groq API key not found. Please set GROQ_API_KEY in your environment or .env file."
            
            try:
                import openai
                client = openai.OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                prompt = (
                    "Correct the following text for both spelling and grammar. "
                    "Only return the corrected text, nothing else.\n\n"
                    f"Text: {sentence}"
                )
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
                return f"Groq LLM correction: {corrected}"
            except Exception as e:
                return f"Groq API error: {e}"
    
    def get_detection_history(self, limit=20):
        """Get detection history from MongoDB"""
        history_docs = list(self.mongo_collection.find({'_id': {'$ne': 'current'}}).sort('timestamp', -1).limit(limit))
        return history_docs
    
    def delete_history_item(self, doc_id):
        """Delete a history item from MongoDB"""
        self.mongo_collection.delete_one({'_id': doc_id})
        return True
    
    def get_last_word_from_sentence(self, sentence):
        """Extract the last word from a sentence"""
        if sentence.strip():
            words = sentence.strip().split()
            return words[-1] if words else ""
        return ""
    
    def record_voice_input(self):
        """Record and convert voice to text"""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                voice_text = recognizer.recognize_google(audio)
                return voice_text
            except sr.UnknownValueError:
                return "Could not understand the audio. Please try again."
            except sr.RequestError as e:
                return f"Could not request results; {e}"
        except ImportError:
            return "Speech recognition not available. Please install SpeechRecognition and pyaudio packages."
        except Exception as e:
            return f"Voice recording error: {e}"
    
    def generate_sign_video(self, text):
        """Generate sign language video from text"""
        if not text.strip():
            return "Please enter some text to generate the video."
        
        try:
            result = subprocess.run([
                sys.executable, "text_to_sign_video.py", text
            ], capture_output=True, text=True)
            time.sleep(1)
            
            if os.path.exists("output_sign_sequence.mp4"):
                with open("output_sign_sequence.mp4", "rb") as video_file:
                    video_bytes = video_file.read()
                return video_bytes
            else:
                return "Video could not be generated. Please try again."
        except Exception as e:
            return f"Video generation error: {e}"
    
    def ask_ai_assistant(self, question):
        """Ask AI assistant using Groq LLM"""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return "Groq API key not found. Please set GROQ_API_KEY in your environment or .env file."
        
        try:
            import openai
            client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            prompt = (
                "Answer the following question as simply as possible, using a maximum of 3 words. "
                "If the question cannot be answered simply, respond with 'Cannot answer'.\n\n"
                f"Question: {question}"
            )
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
            return ai_answer
        except Exception as e:
            return f"Groq API error: {e}"
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return str(timestamp)
    
    def format_short_timestamp(self, timestamp):
        """Format timestamp for short display"""
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%H:%M:%S")
        return str(timestamp)
    
    def get_last_stored_sentence(self):
        """Get the last stored sentence from history (excluding current)"""
        last_doc = self.mongo_collection.find_one(
            {'_id': {'$ne': 'current'}}, 
            sort=[('timestamp', -1)]
        )
        if last_doc and 'sentence' in last_doc:
            return last_doc['sentence']
        return None
    
    def is_consecutive_duplicate(self, new_sentence):
        """Check if the new sentence is the same as the last stored sentence"""
        last_sentence = self.get_last_stored_sentence()
        if last_sentence:
            return new_sentence.strip() == last_sentence.strip()
        return False
    
    def clear_all_history(self):
        """Clear all stored values from MongoDB"""
        try:
            result = self.mongo_collection.delete_many({})
            return f"Successfully deleted {result.deleted_count} documents"
        except Exception as e:
            return f"Error clearing database: {e}"
    
    def start_text_storage(self):
        """Enable automatic text storage during detection"""
        self.should_store_text = True
        return "Text storage enabled. Detected text will be stored automatically."
    
    def stop_text_storage(self):
        """Disable automatic text storage during detection"""
        self.should_store_text = False
        return "Text storage disabled. Detected text will not be stored automatically."
    
    def store_current_text(self):
        """Manually store the current detected text in history"""
        current_sentence = self.get_current_sentence()
        if not current_sentence.strip():
            return "No text to store."
        
        sentence_clean = current_sentence.strip()
        if len(sentence_clean) < 2:
            return "Text must be at least 2 characters long to store."
        
        # Check if this is a consecutive duplicate
        last_doc = self.mongo_collection.find_one(
            {'_id': {'$ne': 'current'}}, 
            sort=[('timestamp', -1)]
        )
        is_duplicate = False
        if last_doc and 'sentence' in last_doc:
            is_duplicate = sentence_clean == last_doc['sentence'].strip()
        
        if is_duplicate:
            return "This text is already stored (consecutive duplicate)."
        
        # Store the text
        from datetime import datetime
        history_doc = {
            'sentence': sentence_clean,
            'timestamp': datetime.now(),
            'full_text': current_sentence,
            'word_count': len(sentence_clean.split()),
            'char_count': len(sentence_clean)
        }
        self.mongo_collection.insert_one(history_doc)
        return f"Successfully stored: '{sentence_clean}'"
    
    def get_storage_status(self):
        """Get current text storage status"""
        return self.should_store_text 