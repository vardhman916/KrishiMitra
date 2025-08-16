# krishi_mitra_ui.py
import streamlit as st
import os
from dotenv import load_dotenv
from tools.Google_search import google_search_tool
from tools.government_scheme import government_scheme_tool
from tools.weather_forecast_tools import get_weather_forecast
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from STT import LanguageSwitchingSTT, MicrophoneStream, RATE, CHUNK
from google.cloud import speech
from langdetect import detect
from googletrans import Translator
from tools.wikidata import wikidata_tool
from tools.other_information import crop_cultivation_tool

# Load environment variables
load_dotenv()

translator = Translator()

# ---- LLM Setup ----
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

# ---- Tools ----
tools = [
    google_search_tool,
    government_scheme_tool,
    get_weather_forecast,
    wikidata_tool,
    crop_cultivation_tool
]

# ---- Agent ----
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
    
)

# ---- Summarization Prompt ----
summary_prompt_template = """
You are **Krishi Mitra**, a helpful and friendly agricultural assistant for farmers in India.

Below is information collected from multiple trusted sources:
{results}

Your job is to summarize and present this information in a **clear, short, and easy-to-understand format for a farmer with basic education**.

Follow these rules strictly:
1. **Separate sections clearly**:  
   - "🌤 Weather Update" (max 4 short bullet points)  
   - "💰 Government Schemes" (max 2 short bullet points)  
   - "🌱 Farming Advice" (max 3 short bullet points, only if relevant)  
2. **Use farmer-friendly language**.  
3. **Give actionable insights** — each point should be advice the farmer can act on today.  
4. give the final output  in the format of which farmer ask his question 
5. Remove any repeated or unnecessary details.  
6. Prioritize **urgent weather alerts** first, then crop-specific guidance, then schemes.  
7. If a section has no relevant info, write "No update available." for that section.

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
    lang_code = detect(user_query)

    # Translate to English for agent if needed
    if lang_code != "en":
        query_en = translator.translate(user_query, src=lang_code, dest="en").text
    else:
        query_en = user_query

    raw_result = agent.invoke(query_en)

    summary_prompt = PromptTemplate(
        input_variables=["results"],
        template=summary_prompt_template
    )

    summary_en = llm1.invoke(summary_prompt.format(results=raw_result)).content

    # Translate back to original language if needed
    if lang_code != "en":
        summary_final = translator.translate(summary_en, src="en", dest=lang_code).text
    else:
        summary_final = summary_en

    return summary_final

def run_voice_mode():
    """Captures speech using Google STT and returns transcription."""
    stt_handler = LanguageSwitchingSTT()
    config = stt_handler.get_config_for_language(stt_handler.current_language)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
        single_utterance=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = stt_handler.client.streaming_recognize(streaming_config, requests)

        transcript = ""
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript.strip()
            if result.is_final:
                break
    return transcript

# ---- Streamlit UI ----
st.set_page_config(page_title="Krishi Mitra", page_icon="🌾", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center; color: green;'>🌾 Krishi Mitra</h1>
    <h3 style='text-align: center; color: #b8860b;'>Your Smart Farming Assistant</h3>
    """,
    unsafe_allow_html=True
)

mode = st.radio("Choose Input Mode:", ["Text", "Voice"], horizontal=True)

if mode == "Text":
    user_input = st.text_input("Ask your farming question in Hindi or English:")
    if st.button("Get Answer"):
        if user_input.strip():
            answer = process_query(user_input)
            st.success(answer)

elif mode == "Voice":
    st.write("Click the button and speak your question.")
    if st.button("🎙 Speak Now"):
        with st.spinner("Listening..."):
            transcript = run_voice_mode()
        if transcript:
            st.write(f"📝 You said: **{transcript}**")
            answer = process_query(transcript)
            st.success(answer)
