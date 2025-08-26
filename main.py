from sarvamai import SarvamAI
import base64
import io
import itertools
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

from tools.Google_search import google_search_tool
from tools.Price_prediction import predictor_tool
from tools.Price_prediction import connected_agent, connected_agent_tool
from tools.government_scheme import government_scheme_tool
from tools.weather_forecast_tools import get_weather_forecast
from tools.wikidata import wikidata_tool
from tools.Pest_info import combined_Pest_tool
from tools.other_information import crop_cultivation_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType

from langchain_core.prompts import PromptTemplate
from STT import LanguageSwitchingSTT, MicrophoneStream, RATE, CHUNK
from google.cloud import speech
from langdetect import detect
from googletrans import Translator
from flask import session
import threading
import logging
import re
import time
from langdetect import detect, LangDetectException

# Language code mapping for Sarvam AI
SARVAM_LANGUAGE_MAP = {
    'hi': 'hi-IN',
    'en': 'en-IN', 
    'ta': 'ta-IN',
    'te': 'te-IN',
    'bn': 'bn-IN',
    'mr': 'mr-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'pa': 'pa-IN',
    'or': 'or-IN'
}


# Load environment variables
load_dotenv()

# Initialize Sarvam AI client
sarvam_client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)
# Quick API key check (using print since logger not ready yet)
api_key = os.getenv("SARVAM_API_KEY")
if api_key:
    print(f"✅ Sarvam API Key loaded successfully: {api_key[:10]}...")
else:
    print("❌ Sarvam API Key not found in .env file")

try:
    sarvam_client = SarvamAI(api_subscription_key=api_key)
    print("✅ Sarvam client initialized successfully")
except Exception as e:
    print(f"❌ Sarvam client initialization failed: {e}")
    sarvam_client = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Initialize translator
translator = Translator()



import re
from langdetect import detect, DetectorFactory, LangDetectException
import logging

logger = logging.getLogger(__name__)
DetectorFactory.seed = 0  # Makes langdetect deterministic


def detect_language_robust(text):
    """Robust language detection with multiple fallbacks for Indian languages"""
    try:
        # Expanded regex to cover all Indic scripts + Urdu/Arabic
        cleaned_text = re.sub(
            r'[^\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF'
            r'\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF'
            r'\u0D00-\u0D7F\u0D80-\u0DFF\u0600-\u06FF\w\s]',
            '',
            text
        ).strip()
        
        if len(cleaned_text) < 3:
            return "en"
        
        # Try langdetect
        detected = detect(cleaned_text)
        
        lang_mapping = {
            'hi': 'hi', 'en': 'en', 'ta': 'ta', 'te': 'te',
            'bn': 'bn', 'mr': 'mr', 'gu': 'gu', 'kn': 'kn',
            'ml': 'ml', 'pa': 'pa', 'ur': 'ur'
        }
        
        return lang_mapping.get(detected, 'en')
    
    except (LangDetectException, Exception) as e:
        logger.warning(f"Language detection failed: {e}")

        # --- Fallback Patterns ---
        patterns = {
            'hi': ['है', 'में', 'का', 'की', 'को', 'से', 'पर', 'और', 'या'],
            'bn': ['কেমন', 'আমি', 'তুমি', 'সে', 'এই', 'ওই', 'কি'],
            'pa': ['ਹੈ', 'ਤੇ', 'ਦਾ', 'ਦੀ', 'ਦੇ', 'ਨੂੰ', 'ਅਤੇ'],
            'mr': ['आहे', 'मध्ये', 'चा', 'ची', 'किंवा', 'आणि'],
            'gu': ['છે', 'અને', 'કરવું', 'કે', 'ના', 'હું', 'તું'],
            'kn': ['ಇದು', 'ಮತ್ತು', 'ಅಥವಾ', 'ಹೆಚ್ಚು', 'ಹೆಸರು'],
            'ta': ['இது', 'அவர்', 'என்', 'உன்', 'மற்றும்', 'அல்லது'],
            'te': ['అది', 'మరియు', 'లేదా', 'నేను', 'నువ్వు'],
            'ml': ['ആണ്', 'എന്ന്', 'എനിക്ക്', 'നിങ്ങൾ', 'അഥവാ'],
            'ur': ['ہے', 'میں', 'اور', 'یا', 'کے', 'سے', 'پر'],
            'en': ['the', 'is', 'and', 'or', 'to', 'of']
        }

        for lang, words in patterns.items():
            if any(word in text for word in words):
                return lang
        
        return 'en'

    """Robust language detection with multiple fallbacks"""
    try:
        # Clean the text first
        cleaned_text = re.sub(r'[^\u0900-\u097F\u0600-\u06FF\w\s]', '', text).strip()
        if len(cleaned_text) < 3:
            return "en"
        
        # Try langdetect first
        detected = detect(cleaned_text)
        
        # Map some common codes
        lang_mapping = {
            'hi': 'hi',
            'en': 'en', 
            'ta': 'ta',
            'te': 'te',
            'bn': 'bn',
            'mr': 'mr',
            'gu': 'gu',
            'kn': 'kn',
            'ml': 'ml',
            'pa': 'pa',
            'ur': 'ur'
        }
        
        return lang_mapping.get(detected, 'en')
        
    except (LangDetectException, Exception) as e:
        logger.warning(f"Language detection failed: {e}")
        
        # Fallback: Check for common Hindi/Indian language patterns
        hindi_patterns = ['है', 'में', 'का', 'की', 'को', 'से', 'पर', 'और', 'या']
        if any(pattern in text for pattern in hindi_patterns):
            return 'hi'
        
        # Default to English
        return 'en'


def safe_translate(text, src_lang, dest_lang, max_retries=2):
    """Safe translation with retry logic"""
    for attempt in range(max_retries):
        try:
            if src_lang == dest_lang:
                return text
            
            # Initialize fresh translator instance
            translator_instance = Translator()
            result = translator_instance.translate(text, src=src_lang, dest=dest_lang)
            
            if result and result.text:
                return result.text
            else:
                logger.warning(f"Translation attempt {attempt + 1} returned empty result")
                
        except Exception as e:
            logger.error(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All translation attempts failed, returning original text")
                return text
            
            # Wait before retry
            time.sleep(0.5)
    
    return text
 
# Global variables to store LLM instances
llm = None
llm1 = None
agent = None

def initialize_llm_models():
    """Initialize LLM models with error handling"""
    global llm, llm1
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )
        llm1 = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY1"),
            temperature=0.3
        )
        logger.info("LLM models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        return False

def initialize_agent_system():
    """Initialize agent with tools"""
    global agent
    try:
        if llm is None:
            logger.error("LLM not initialized, cannot create agent")
            return False
            
        tools = [
            google_search_tool,
            government_scheme_tool,
            get_weather_forecast,
            combined_Pest_tool,
            wikidata_tool,
            crop_cultivation_tool,
            connected_agent_tool,
            predictor_tool
        ]
        
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True
        )
        logger.info("Agent initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        return False




def clean_response_text(text):

    def remove_repetitions(text):
        """Remove consecutive repeated words and short phrases from text (works for all languages)."""
        # Remove repeated words (e.g., 'लिए लिए लिए' -> 'लिए')
        text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)
        # Remove repeated short phrases (e.g., 'में हल हल मध मध' -> 'में हल मध')
        text = re.sub(r'(\b\w+\b(?: [\w\u0900-\u097F]+){0,2})(?: \1\b)+', r'\1', text)
        # Remove repeated lines
        lines = text.splitlines()
        new_lines = []
        for line in lines:
            if not new_lines or line.strip() != new_lines[-1].strip():
                new_lines.append(line)
        return '\n'.join(new_lines)
        """Remove emoticons, asterisks, and other unwanted characters from response"""
    try:
        # Remove emoticons (Unicode emoji ranges)
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"  # other symbols
                                   u"\U000024C2-\U0001F251"  # enclosed characters
                                   "]+", flags=re.UNICODE)
        
        # Remove asterisks and other formatting characters
        text = emoji_pattern.sub(r'', text)
        text = re.sub(r'\*+', '', text)  # Remove asterisks
        text = re.sub(r'#+', '', text)   # Remove hash symbols
        text = re.sub(r'_{2,}', '', text)  # Remove multiple underscores
        text = re.sub(r'-{3,}', '', text)  # Remove multiple dashes
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove extra blank lines
        text = re.sub(r'[ \t]+', ' ', text)       # Remove extra spaces/tabs
        text = text.strip()
        
        return text
    except Exception as e:
        logger.error(f"Error cleaning response text: {e}")
        return text

def clean_response_simple(response):
    """Simple cleaning using regex to remove debugging info"""
    # Remove json patterns and debugging info
    response = re.sub(r'json\s*{.*?}', '', response, flags=re.DOTALL)
    response = re.sub(r'Okay, I understand\..*?farmers\.', '', response, flags=re.DOTALL)
    
    # Remove "Response:" pattern
    response = re.sub(r'^Response:\s*', '', response, flags=re.MULTILINE)
    
    # Remove any remaining brackets or quotes at start/end
    response = response.strip('{}[]"\'')
    
    return response.strip()


summary_prompt_template = """
You are **Krishi Mitra**, a helpful agricultural assistant for farmers.

Information from tools:
{results}

CRITICAL MEMORY INSTRUCTION: The user has previously shared personal information stored in memory. When they refer to "my crop", "my area", "my location", or "my farm", you MUST use their remembered information (crop types, location, farming details) to provide specific advice. Do not ask them to repeat information they've already provided.


IMPORTANT: You have access to user's remembered information and conversation history. Use this context to provide more personalized and relevant advice.

Format this into clear sections with proper spacing:

🌾 **Market Price Information**
- Current prices and forecasts
- Buy/sell recommendations

🌤️ **Weather Updates** (if asked)
- Today's weather conditions
- Farming impact

💰 **Government Schemes** (if asked)  
- Available schemes and deadlines
- Application process

🌱 **Farming Advice** (if asked)
- Practical farming tips
- Seasonal recommendations

🐛 **Pest Information** (if asked)
- Pest identification and control

Rules:
1. Use simple, clear language
2. Add blank line between each section
3. Include only relevant sections
4. No debugging text or JSON
5. No emoticons except the section headers
6. Make recommendations actionable

Respond in the same language as the user's question.
"""

def process_query(user_query):
    """Handles multi-language input, processes query, and returns farmer-friendly summary with memory."""
    try:
        if agent is None:
            logger.error("Agent not initialized")
            return "I'm sorry, the system is not ready. Please try again later."

        # Store conversation in memory
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        # Add user query to conversation history
        session['conversation_history'].append({
            'type': 'user',
            'content': user_query[:100],  # Limit length
            'timestamp': time.time()
        })

        # Detect language
        lang_code = detect_language_robust(user_query)
        logger.info(f"Detected language: {lang_code}")

        # Get memory context
        memory_context = ""
        if 'memory_facts' in session and session['memory_facts']:
            memory_context = f"\n\nRemembered user information: {'; '.join(session['memory_facts'][-5:])}"  # Last 5 facts
        
        recent_conversations = ""
        if len(session['conversation_history']) > 1:
            recent_conversations = "\n\nRecent conversation context: " + "; ".join([
                f"{conv['type']}: {conv['content'][:50]}" 
                for conv in session['conversation_history'][-4:-1]  # Last 3 conversations excluding current
            ])

        # Translate to English for agent if needed
        query_en = user_query
        if lang_code != "en":
            query_en = safe_translate(user_query, lang_code, "en")
            logger.info(f"Translated query: {query_en}")

        # # Add memory context to query
        # enhanced_query = query_en + memory_context + recent_conversations


        # Create a more structured memory context
        memory_prompt = f"""
        IMPORTANT CONTEXT - Remember this information about the user:
        {memory_context}

        Recent conversation context:
        {recent_conversations}

        User's current question: {query_en}

        Please use the remembered information to provide personalized advice. If the user asks about "my crop" or "my area", refer to their previously mentioned crop types and location.
        """

        enhanced_query = memory_prompt








        # Process with agent
        try:
            raw_result = agent.invoke(enhanced_query)
            
            # ADD CLEANING HERE - Clean the agent response immediately
            if hasattr(raw_result, 'content'):
                cleaned_result = clean_response_simple(raw_result.content)
            elif isinstance(raw_result, str):
                cleaned_result = clean_response_simple(raw_result)
            else:
                cleaned_result = clean_response_simple(str(raw_result))
            
            logger.info("Agent processing completed")
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return "I'm sorry, I couldn't process your request right now. Please try again later."

        # Create summary
        if llm1 is None:
            logger.error("Summary LLM not available")
            return "I'm sorry, I couldn't generate a summary. Please try again later."

        try:
            summary_prompt = PromptTemplate(
                input_variables=["results"],
                template=summary_prompt_template
            )

            # # Use the cleaned result instead of raw_result
            # summary_response = llm1.invoke(summary_prompt.format(results=cleaned_result))

            # Include memory in summary generation
            full_context = f"User Memory: {memory_context}\n\nAgent Results: {cleaned_result}"
            summary_response = llm1.invoke(summary_prompt.format(results=full_context))




            summary_en = summary_response.content
            
            # Clean the summary response
            summary_en = clean_response_simple(summary_en)  # First remove debugging
            summary_en = clean_response_text(summary_en)    # Then remove formatting
            
            logger.info("Summary generated")

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "I'm sorry, I couldn't generate a proper summary. Please try again later."

        # Translate back to original language if needed
        summary_final = summary_en
        if lang_code != "en":
            summary_final = safe_translate(summary_en, "en", lang_code)
            logger.info(f"Response translated back to {lang_code}")
            # Clean the translated text as well
            summary_final = clean_response_text(summary_final)

        # Store assistant response in memory
        session['conversation_history'].append({
            'type': 'assistant',
            'content': summary_final[:100],  # Limit length
            'timestamp': time.time()
        })

        # Keep only last 20 conversations to avoid session bloat
        if len(session['conversation_history']) > 20:
            session['conversation_history'] = session['conversation_history'][-20:]
        
        session.modified = True

        # Remove repetitions in the final summary
        summary_final = remove_repetitions(summary_final)
        return summary_final

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."

def generate_audio_response(text, language_code):
    """Generate audio using Sarvam AI TTS with chunking for long text"""
    try:
        if sarvam_client is None:
            logger.error("Sarvam client not available")
            return None





        # Map language code to Sarvam format
        sarvam_lang = SARVAM_LANGUAGE_MAP.get(language_code, 'hi-IN')
        
        # Define chunk size (Sarvam typically supports ~500-1000 characters)
        MAX_CHUNK_SIZE = 500
        
        # If text is short enough, process normally
        if len(text) <= MAX_CHUNK_SIZE:
            return generate_single_audio_chunk(text, sarvam_lang)
        
        # Split long text into chunks
        chunks = split_text_into_chunks(text, MAX_CHUNK_SIZE)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        audio_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
            
            chunk_audio = generate_single_audio_chunk(chunk.strip(), sarvam_lang)
            if chunk_audio:
                audio_chunks.append(chunk_audio)
            else:
                logger.error(f"Failed to generate audio for chunk {i+1}")
        
        if not audio_chunks:
            logger.error("No audio chunks were generated")
            return None
        
        # If only one chunk, return it directly
        if len(audio_chunks) == 1:
            return audio_chunks[0]
        
        # Combine multiple audio chunks
        try:
            combined_audio = combine_audio_chunks(audio_chunks)
            logger.info("✅ Combined audio generated successfully")
            return combined_audio
        except Exception as e:
            logger.error(f"Error combining audio chunks: {e}")
            # Fallback: return first chunk
            return audio_chunks[0]
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return None

# def generate_single_audio_chunk(text, sarvam_lang):
#     """Generate audio for a single text chunk"""
#     try:
#         response = sarvam_client.text_to_speech.convert(
#             text=text,
#             target_language_code=sarvam_lang,
#             speaker="karun",
#             pitch=0,
#             pace=1,
#             loudness=1,
#             speech_sample_rate=22050,
#             enable_preprocessing=True,
#             model="bulbul:v2"
#         )
        
#         # The correct attribute is 'audios'
#         if hasattr(response, 'audios') and response.audios:
#             # audios is likely a list, so take the first one
#             audio_data = response.audios[0] if isinstance(response.audios, list) else response.audios
            
#             # Handle different audio data formats
#             if isinstance(audio_data, str):
#                 # Already base64 encoded string
#                 return audio_data
#             elif isinstance(audio_data, bytes):
#                 # Convert bytes to base64
#                 return base64.b64encode(audio_data).decode('utf-8')
#             else:
#                 logger.error(f"Unexpected audio data type: {type(audio_data)}")
#                 return None
#         else:
#             logger.error("No audio data found in response.audios")
#             return None
        
#     except Exception as e:
#         logger.error(f"Single chunk TTS generation failed: {e}")
#         return None

def generate_single_audio_chunk(text, sarvam_lang):
    """Generate audio for a single text chunk"""
    try:
        if sarvam_client is None:
            logger.error("Sarvam client not initialized")
            return None
            
        response = sarvam_client.text_to_speech.convert(
            text=text,
            target_language_code=sarvam_lang,
            speaker="karun",
            pitch=0,
            pace=1,
            loudness=1,
            speech_sample_rate=22050,
            enable_preprocessing=True,
            model="bulbul:v2"
        )
        
        # Handle different response formats
        if hasattr(response, 'audio') and response.audio:
            audio_data = response.audio
        elif hasattr(response, 'audios') and response.audios:
            audio_data = response.audios[0] if isinstance(response.audios, list) else response.audios
        else:
            logger.error(f"No audio data in response. Response attributes: {dir(response)}")
            return None
            
        # Handle different audio data formats
        if isinstance(audio_data, str):
            return audio_data
        elif isinstance(audio_data, bytes):
            return base64.b64encode(audio_data).decode('utf-8')
        else:
            logger.error(f"Unexpected audio data type: {type(audio_data)}")
            return None
        
    except Exception as e:
        logger.error(f"Single chunk TTS generation failed: {e}")
        return None

def split_text_into_chunks(text, max_size):
    """Split text into chunks while preserving sentence boundaries"""
    # Split by sentences first
    sentences = re.split(r'[।|।|.|!|?|\n]', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence exceeds max size, start new chunk
        if current_chunk and len(current_chunk + " " + sentence) > max_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                # Single sentence is too long, split by words
                words = sentence.split()
                for word in words:
                    if len(current_chunk + " " + word) > max_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = word
                        else:
                            # Single word is too long, force it
                            chunks.append(word)
                    else:
                        current_chunk += " " + word if current_chunk else word
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def combine_audio_chunks(audio_chunks):
    """Combine multiple base64 audio chunks into one"""
    try:
        # Since we're dealing with base64 strings, we need to decode them,
        # combine the binary data, then re-encode
        
        combined_audio_bytes = b""
        
        for audio_b64 in audio_chunks:
            # Decode base64 to bytes
            audio_bytes = base64.b64decode(audio_b64)
            combined_audio_bytes += audio_bytes
        
        # Re-encode combined audio to base64
        combined_b64 = base64.b64encode(combined_audio_bytes).decode('utf-8')
        return combined_b64
        
    except Exception as e:
        logger.error(f"Error combining audio chunks: {e}")
        # Fallback: return first chunk
        return audio_chunks[0] if audio_chunks else None

def run_voice_mode():
    """Captures speech using Google STT and returns transcription."""
    import time
    try:
        from flask import session
        logger.info("Initializing STT handler...")
        stt_handler = LanguageSwitchingSTT()
        # Use language from session if available
        selected_lang = session.get('selected_language', None)
        if selected_lang:
            stt_handler.current_language = selected_lang
            logger.info(f"Using user-selected language: {selected_lang}")
        else:
            logger.info(f"Using default language: {stt_handler.current_language}")
        config = stt_handler.get_config_for_language(stt_handler.current_language)
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False
        )
        
        logger.info("Starting microphone stream...")

        logger.info("Starting microphone stream...")
        with MicrophoneStream(RATE, CHUNK) as stream:
            logger.info("Microphone stream started")
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            logger.info("Starting streaming recognition...")
            responses = stt_handler.client.streaming_recognize(streaming_config, requests)

            transcript = ""
            response_count = 0
            for response in responses:
                response_count += 1
                logger.info(f"Received response {response_count}")
                
                if not response.results:
                    logger.info("No results in response")
                    continue
                    
                result = response.results[0]
                if not result.alternatives:
                    logger.info("No alternatives in result")
                    continue
                    
                transcript = result.alternatives[0].transcript.strip()
                logger.info(f"Transcript: '{transcript}', is_final: {result.is_final}")
                
                if result.is_final and transcript:
                    logger.info(f"Final transcript received: {transcript}")
                    break
            
            logger.info(f"Voice transcript: {transcript}")
        return transcript

    except Exception as e:
        logger.error(f"Error in voice mode: {e}")
        return ""

def remove_repetitions(text):
    """Remove consecutive repeated words and short phrases from text (works for all languages)."""
    # Remove repeated words (e.g., 'लिए लिए लिए' -> 'लिए')
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)
    # Remove repeated short phrases (e.g., 'में हल हल मध मध' -> 'में हल मध')
    text = re.sub(r'(\b\w+\b(?: [\w\u0900-\u097F]+){0,2})(?: \1\b)+', r'\1', text)
    # Remove repeated lines
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if not new_lines or line.strip() != new_lines[-1].strip():
            new_lines.append(line)
    return '\n'.join(new_lines)


# Initialize systems on startup
def initialize_systems():
    """Initialize all systems with proper error handling"""
    logger.info("Initializing Krishi Mitra systems...")
    
    llm_success = initialize_llm_models()
    if not llm_success:
        logger.error("Failed to initialize LLM models")
        return False
    
    agent_success = initialize_agent_system()
    if not agent_success:
        logger.error("Failed to initialize agent")
        return False
    
    logger.info("All systems initialized successfully")
    return True
    
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/generate_audio', methods=['POST'])
def handle_generate_audio():
    """Generate audio for text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'hi')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        audio_data = generate_audio_response(text, language)
        
        if audio_data:
            return jsonify({
                'success': True,
                'audio_data': audio_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Audio generation failed'
            })
            
    except Exception as e:
        logger.error(f"Error in generate_audio route: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/set_language', methods=['POST'])
def set_language():
    data = request.get_json()
    lang_code = data.get('language')
    if lang_code:
        session['selected_language'] = lang_code
        return jsonify({'success': True, 'language': lang_code})
    return jsonify({'success': False, 'error': 'No language provided'}), 400
@app.route('/process_query', methods=['POST'])
def handle_process_query():
    """Handle text/voice query processing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            })
            
        user_query = data.get('query', '').strip()
        mode = data.get('mode', 'text')
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            })

        logger.info(f"Processing {mode} query: {user_query}")
        
        # Check if systems are initialized
        if agent is None or llm is None or llm1 is None:
            return jsonify({
                'success': False,
                'error': 'System is not ready. Please refresh the page and try again.'
            })
        
        # Process the query
        response = process_query(user_query)
        # Generate audio for the response
        detected_lang = detect_language_robust(user_query)
        audio_data = generate_audio_response(response, detected_lang)
        
        return jsonify({
            'success': True,
            'response': response,
            'audio_data': audio_data,
            'language': detected_lang,
            'mode': mode
        })

    except Exception as e:
        logger.error(f"Error in process_query route: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again.'
        })

@app.route('/voice_input', methods=['POST'])
def handle_voice_input():
    """Handle voice input capture with language detection"""
    try:
        logger.info("Voice input endpoint called")
        
        # Check if Google Cloud credentials are available
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.error("Google Cloud credentials not found")
            return jsonify({
                'success': False,
                'error': 'Voice recognition service not configured'
            })
        
        logger.info("Processing voice input...")
        
        # Run voice capture
        transcript = run_voice_mode()
        
        if transcript:
            # Detect language of the transcript
            detected_lang = detect_language_robust(transcript)
            logger.info(f"Voice transcript: {transcript}, detected language: {detected_lang}")
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'detected_language': detected_lang
            })
        else:
            logger.warning("No transcript received from voice input")
            return jsonify({
                'success': False,
                'error': 'No speech detected or microphone access denied'
            })

    except Exception as e:
        logger.error(f"Error in voice_input route: {e}")
        return jsonify({
            'success': False,
            'error': 'Voice input failed. Please check your microphone permissions.'
        })




# Memory Management Routes
@app.route('/get_memory', methods=['GET'])
def get_memory():
    """Get stored memory data"""
    try:
        # Initialize session memory if not exists
        if 'memory_facts' not in session:
            session['memory_facts'] = []
        if 'conversation_history' not in session:
            session['conversation_history'] = []
            
        return jsonify({
            'success': True,
            'memory': {
                'facts': session.get('memory_facts', []),
                'conversation': session.get('conversation_history', [])[-10:]  # Last 10 conversations
            }
        })
    except Exception as e:
        logger.error(f"Error getting memory: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_memory', methods=['POST'])
def add_memory():
    """Add new memory fact"""
    try:
        data = request.get_json()
        memory_text = data.get('memory', '').strip()
        
        if not memory_text:
            return jsonify({'success': False, 'error': 'No memory text provided'})
        
        # Initialize if not exists
        if 'memory_facts' not in session:
            session['memory_facts'] = []
            
        # Add to memory facts
        session['memory_facts'].append(memory_text)
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Memory added successfully'})
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    """Clear all memory"""
    try:
        session['memory_facts'] = []
        session['conversation_history'] = []
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Memory cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        return jsonify({'success': False, 'error': str(e)})

# @app.route('/health', methods=['GET'])  # ← This line should already exist


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'llm_initialized': llm is not None,
            'llm1_initialized': llm1 is not None,
            'agent_initialized': agent is not None,
            'overall_status': 'healthy' if all([llm, llm1, agent]) else 'degraded'
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

# Initialize systems before running the app
@app.before_request
def startup():
    """Initialize systems on first request"""
    success = initialize_systems()
    if not success:
        logger.error("Failed to initialize systems on startup")

if __name__ == '__main__':
    logger.info("Starting Krishi Mitra application...")
    success = initialize_systems()
    if not success:
        logger.error("Failed to initialize systems. Exiting...")
        exit(1)

    logger.info("Starting Flask server...")
    port = int(os.environ.get('PORT', 5000))  # ✅ Add this line
    app.run(debug=True, host='0.0.0.0', port=port)  # ✅ Update this line
