import itertools
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

from tools.Google_search import google_search_tool
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Initialize translator
translator = Translator()






def detect_language_robust(text):
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
            crop_cultivation_tool

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









# Updated summarization prompt without emoticons
summary_prompt_template = """
You are **Krishi Mitra**, a helpful and friendly agricultural assistant for farmers in India.

Below is information collected from multiple trusted sources:
{results}

Your job is to summarize and present this information in a clear, short with full information, and easy-to-understand format for a farmer with basic education.

Follow these rules strictly:
1. Identify which of these categories the farmer's question relates to:  
   - 🌤 Weather Update" (max 4 short bullet points)  
   - 💰 Government Schemes" (max 2 short bullet points)  
   - 🌱 Farming Advice" (max 3 short bullet points, only if relevant)   
2. Include ONLY the categories the farmer asked about.  
3. If the farmer asked about multiple topics, include all relevant categories.  
4. Do NOT add "No update available" for categories that were not asked about.  
5. Use farmer-friendly, simple language  
6. Each point must be clear, short, and actionable today.  
7. Weather alerts come first if included, then schemes, then farming advice.  
8. Remove any repeated or unnecessary details.  
9. No emoticons, asterisks, or special symbols.  
10. Detect the language of the farmer's question and give the final response in that same language.
Output Format Example:
🌤 **Weather Update**  
- Rain expected in the next 24 hours in [region].  
- Temperature around 28°C; humidity high.

💰 **Government Schemes**  
- Apply for the PM-Kisan scheme online before [date].  

🌱 **Farming Advice**  
- Avoid watering wheat crops today due to rainfall forecast.
"""






def process_query(user_query):
    """Handles multi-language input, processes query, and returns farmer-friendly summary."""
    try:
        if agent is None:
            logger.error("Agent not initialized")
            return "I'm sorry, the system is not ready. Please try again later."

        # Detect language
        lang_code = detect_language_robust(user_query)
        logger.info(f"Detected language: {lang_code}")

        # Translate to English for agent if needed
        query_en = user_query
        if lang_code != "en":
            query_en = safe_translate(user_query, lang_code, "en")
            logger.info(f"Translated query: {query_en}")

        # Process with agent
        try:
            raw_result = agent.invoke(query_en)
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

            summary_response = llm1.invoke(summary_prompt.format(results=raw_result))
            summary_en = summary_response.content
            logger.info("Summary generated")
            
            # Clean the response text to remove emoticons and asterisks
            summary_en = clean_response_text(summary_en)

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

    # Remove repetitions in the final summary
        summary_final = remove_repetitions(summary_final)
        return summary_final

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."




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

# ---- Flask Routes ----

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

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
        
        return jsonify({
            'success': True,
            'response': response,
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
