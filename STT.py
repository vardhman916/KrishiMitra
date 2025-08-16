import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'D:\open_AI_api\divine-display-461906-u9.json'

import pyaudio
from google.cloud import speech
from six.moves import queue
import re
 
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Language commands and their codes
LANGUAGE_COMMANDS = {
    # English commands
    'english': 'en-IN',
    'hindi': 'hi-IN',
    'bengali': 'bn-IN',
    'tamil': 'ta-IN',
    'telugu': 'te-IN',
    'marathi': 'mr-IN',
    'gujarati': 'gu-IN',
    'kannada': 'kn-IN',
    'malayalam': 'ml-IN',
    'punjabi': 'pa-Guru-IN',
    'odia': 'or-IN',
    'assamese': 'as-IN',
    'urdu': 'ur-IN',
    'nepali': 'ne-IN',
    'sanskrit': 'sa-IN',
    
    # Hindi commands (for Hindi speakers)
    'अंग्रेजी': 'en-IN',
    'हिंदी': 'hi-IN',
    'बंगाली': 'bn-IN',
    'तमिल': 'ta-IN',
    'तेलुगु': 'te-IN',
    'मराठी': 'mr-IN',
    'गुजराती': 'gu-IN',
    'कन्नड़': 'kn-IN',
    'मलयालम': 'ml-IN',
    'पंजाबी': 'pa-Guru-IN',
    'उड़िया': 'or-IN',
    'असमिया': 'as-IN',
    'उर्दू': 'ur-IN',
    'नेपाली': 'ne-IN',
    'संस्कृत': 'sa-IN',
}

# Language code to name mapping
LANGUAGE_NAMES = {
    'hi-IN': 'Hindi',
    'en-IN': 'English (Indian)',
    'bn-IN': 'Bengali', 
    'ta-IN': 'Tamil',
    'te-IN': 'Telugu',
    'mr-IN': 'Marathi',
    'gu-IN': 'Gujarati',
    'kn-IN': 'Kannada',
    'ml-IN': 'Malayalam',
    'pa-Guru-IN': 'Punjabi',
    'or-IN': 'Odia',
    'as-IN': 'Assamese',
    'ur-IN': 'Urdu',
    'ne-IN': 'Nepali',
    'sa-IN': 'Sanskrit',
}

class LanguageSwitchingSTT:
    def __init__(self):
        self.current_language = 'hi-IN'  # Default to Hindi
        self.client = speech.SpeechClient()
        self.language_switching = False
        
    def detect_language_command(self, text):
        """Check if the text contains a language switching command."""
        text_lower = text.lower().strip()
        
        # Check for exact language commands
        for command, lang_code in LANGUAGE_COMMANDS.items():
            if command in text_lower:
                return lang_code
        return None
    
    def get_config_for_language(self, language_code):
        """Get speech recognition config for specific language."""
        # Languages that only support the default model (not latest_short)
        default_model_languages = {
            'pa-Guru-IN', 'or-IN', 'as-IN', 'ur-IN', 'ne-IN', 'sa-IN',
            # Add more if you find others unsupported by 'latest_short'
        }
        model = 'default' if language_code in default_model_languages else 'latest_short'
        return speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model=model,
        )

class MicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks."""
    
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Generator function to yield audio chunks from the buffer."""
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

def display_transcription_with_language_switching(responses, stt_handler):
    """Display live transcription results with language command detection."""
    num_chars_printed = 0
    
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        confidence = getattr(result.alternatives[0], 'confidence', 0)
        
        # Check for language switching command
        if result.is_final:
            detected_lang = stt_handler.detect_language_command(transcript)
            if detected_lang and detected_lang != stt_handler.current_language:
                stt_handler.current_language = detected_lang
                language_name = LANGUAGE_NAMES.get(detected_lang, detected_lang)
                print(f"\n🔄 Switching to: {language_name} ({detected_lang})")
                print("🎤 Now speak in the selected language...")
                print("-" * 60)
                return True  # Signal to restart with new language
        
        overwrite_chars = " " * max(0, num_chars_printed - len(transcript))

        if not result.is_final:
            # Show interim results
            print(f"\rListening: {transcript}{overwrite_chars}", end="", flush=True)
            num_chars_printed = len(transcript)
        else:
            # Show final results
            confidence_text = f" [Confidence: {confidence:.2f}]" if confidence > 0 else ""
            print(f"\rFinal: {transcript}{confidence_text}{overwrite_chars}")
            num_chars_printed = 0
    
    return False

def start_language_switching_recognition():
    """Start speech recognition with language command switching."""
    
    stt_handler = LanguageSwitchingSTT()
    
    while True:
        try:
            # Get config for current language
            config = stt_handler.get_config_for_language(stt_handler.current_language)
            
            streaming_config = speech.StreamingRecognitionConfig(
                config=config,
                interim_results=True,
                single_utterance=False,
            )

            # Start microphone stream and recognition
            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                responses = stt_handler.client.streaming_recognize(streaming_config, requests)
                
                # Process responses and check for language switching
                language_switched = display_transcription_with_language_switching(responses, stt_handler)
                
                if not language_switched:
                    break  # Exit if no language switch occurred
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Restarting recognition...")
            continue

def display_startup_info():
    """Display application startup information."""
    print("=" * 70)
    print("🎤 LANGUAGE COMMAND-BASED SPEECH-TO-TEXT 🎤")
    print("=" * 70)
    
    print("\n✨ FEATURES:")
    print("   • Smart language switching via voice commands")
    print("   • Support for 15 Indian languages")
    print("   • Real-time transcription")
    print("   • Confidence scoring")
    
    print(f"\n🌐 SUPPORTED LANGUAGES:")
    print("   Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati")
    print("   Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu, Nepali, Sanskrit")
    
    print("\n🎯 HOW TO SWITCH LANGUAGES:")
    print("   • Say the language name to switch (e.g., 'Hindi', 'Tamil', 'English')")
    print("   • You can also use Hindi names (e.g., 'हिंदी', 'तमिल', 'अंग्रेजी')")
    print("   • After saying the language name, start speaking in that language")
    
    print("\n📝 EXAMPLE USAGE:")
    print("   🗣️  'Hindi' → Switches to Hindi")
    print("   🗣️  'अब मैं हिंदी में बात कर रहा हूँ'")
    print("   🗣️  'Tamil' → Switches to Tamil")  
    print("   🗣️  'இப்போது நான் தமிழில் பேசுகிறேன்'")
    print("   🗣️  'English' → Switches to English")
    print("   🗣️  'Now I am speaking in English'")
    
    print("\n💡 TIPS:")
    print("   • Clearly say the language name before switching")
    print("   • Wait for the language switch confirmation")
    print("   • Press Ctrl+C to exit")
    
    print("\n" + "=" * 70)

def main():
    """Main function to run the language command-based speech recognition."""
    try:
        # Display startup information
        display_startup_info()
        
        input("\nPress ENTER to start listening...")
        
        print(f"\n🎤 Listening in Hindi (Default)...")
        print("💬 Say any language name to switch (e.g., 'English', 'Tamil', 'हिंदी')")
        print("=" * 60)
        
        # Start language switching recognition
        start_language_switching_recognition()
        
    except KeyboardInterrupt:
        print(f"\n\n✅ Speech recognition stopped.")
        print("Thank you for using Language Command-Based Speech-to-Text! 🙏")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   • Check your microphone permissions")
        print("   • Ensure Google Cloud credentials are set correctly")
        print("   • Speak clearly when saying language names")

if __name__ == "__main__":
    main()