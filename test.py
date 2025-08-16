#!/usr/bin/env python3
"""
STT Test Script - Run this to test your speech-to-text setup
"""

import os
import sys
from google.cloud import translate

# Test 1: Check Google Cloud credentials
print("=== TESTING GOOGLE CLOUD CREDENTIALS ===")
creds_path = r'D:\open_AI_api\divine-display-461906-u9.json'
if creds_path:
    print(f"✅ Credentials path: {creds_path}")
    if os.path.exists(creds_path):
        print("✅ Credentials file exists")
    else:
        print("❌ Credentials file does not exist")
        sys.exit(1)
else:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
    sys.exit(1)

# Test 2: Check microphone access
print("\n=== TESTING MICROPHONE ACCESS ===")
try:
    import pyaudio
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print(f"✅ Found {device_count} audio devices")
    
    # List input devices
    for i in range(device_count):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  Input Device {i}: {info['name']}")
    
    p.terminate()
except Exception as e:
    print(f"❌ Microphone test failed: {e}")
    sys.exit(1)

# Test 3: Test Google Cloud Speech Client
print("\n=== TESTING GOOGLE CLOUD SPEECH CLIENT ===")
try:
    from google.cloud import speech
    client = speech.SpeechClient()
    print("✅ Google Speech Client initialized successfully")
except Exception as e:
    print(f"❌ Google Speech Client failed: {e}")
    sys.exit(1)

# Test 4: Test basic speech recognition
print("\n=== TESTING BASIC SPEECH RECOGNITION ===")
try:
    from STT import LanguageSwitchingSTT, MicrophoneStream, RATE, CHUNK
    from google.cloud import speech
    from langdetect import detect
    from googletrans import Translator
    
    translator = Translator()
    
    def test_capture():
        print("🎤 Starting 5-second test recording...")
        print("📢 Say something in Hindi or English NOW!")
        
        stt_handler = LanguageSwitchingSTT()
        
        # Simple config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code='hi-IN',
            enable_automatic_punctuation=True,
            model='latest_short',
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False,
        )
        
        try:
            with MicrophoneStream(RATE, CHUNK) as stream:
                print("🔴 Recording started...")
                audio_generator = stream.generator()
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )
                
                responses = stt_handler.client.streaming_recognize(streaming_config, requests)
                
                transcript_found = False
                for response in responses:
                    if not response.results:
                        continue
                    
                    result = response.results[0]
                    if not result.alternatives:
                        continue
                    
                    transcript = result.alternatives[0].transcript
                    
                    if result.is_final:
                        print(f"✅ Final transcript: '{transcript}'")
                        
                        # Test language detection
                        try:
                            lang_code = detect(transcript)
                            print(f"✅ Detected language: {lang_code}")
                        except Exception as e:
                            print(f"⚠️ Language detection failed: {e}")
                            lang_code = 'hi'
                        
                        # Test translation
                        if lang_code != 'en':
                            try:
                                english_text = translator.translate(transcript, src=lang_code, dest='en').text
                                print(f"✅ English translation: '{english_text}'")
                            except Exception as e:
                                print(f"⚠️ Translation failed: {e}")
                        
                        transcript_found = True
                        break
                    else:
                        print(f"🔄 Interim: '{transcript}'")
                
                if not transcript_found:
                    print("❌ No final transcript received")
                    
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return False
        
        return transcript_found
    
    # Run the test
    success = test_capture()
    if success:
        print("\n🎉 STT TEST PASSED! Your setup is working.")
    else:
        print("\n❌ STT TEST FAILED!")
        
except Exception as e:
    print(f"❌ STT test setup failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")