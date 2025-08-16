# tts.py
import os
from google.cloud import texttospeech
import playsound
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'D:\open_AI_api\gentle-respect-454115-i3-11a77ced5856.json'
class TextToSpeech:
    def __init__(self):
        # Make sure GOOGLE_APPLICATION_CREDENTIALS is set
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS is not set.")

        self.client = texttospeech.TextToSpeechClient()

    def speak(self, text, language_code="en-IN"):
        """Convert given text to speech and play it."""
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Save audio
        output_file = "response.mp3"
        with open(output_file, "wb") as out:
            out.write(response.audio_content)

        # Play audio
        playsound.playsound(output_file)

        # Optional: delete file after playing
        os.remove(output_file)
