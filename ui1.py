# # import streamlit as st
# # from PIL import Image
# # import base64
# # import os

# # # --- PAGE CONFIG ---
# # st.set_page_config(page_title="Krishi Mitra", layout="wide")

# # # --- LOAD BACKGROUND ---
# # def add_bg_from_local(image_file):
# #     if not os.path.exists(image_file):
# #         st.error(f"Background image not found: {image_file}")
# #         return
# #     with open(image_file, "rb") as file:
# #         encoded_string = base64.b64encode(file.read()).decode()
# #     st.markdown(
# #         f"""
# #         <style>
# #         .stApp {{
# #             background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
# #                         url("data:image/jpg;base64,{encoded_string}");
# #             background-size: contain;
# #             background-position: center;
# #         }}
# #         h1, .stTitle {{
# #             color: #ffffff !important;
# #             text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
# #         }}
# #         .stMarkdown p {{
# #             color: #f0f0f0 !important;
# #             text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
# #         }}
# #         .voice-button-container {{
# #             display: flex;
# #             align-items: center;
# #             justify-content: center;
# #             height: 140px;
# #         }}
# #         </style>
# #         """,
# #         unsafe_allow_html=True
# #     )

# # # Load background
# # add_bg_from_local("D:/open_AI_API/static/image.jpg")

# # # --- HEADER ---
# # st.markdown(
# #     """
# #     <h1 style="text-align:center; color:white; font-size:50px; font-weight:bold;">
# #     🌾 Krishi Mitra
# #     </h1>
# #     <p style="text-align:center; color:white; font-size:18px;">
# #     Your AI-powered agriculture assistant — Talk or Type for Instant Advice
# #     </p>
# #     """,
# #     unsafe_allow_html=True
# # )

# # # --- INPUT SECTION ---
# # col1, col2 = st.columns([3, 1])

# # with col1:
# #     user_input = st.text_area("💬 Type your query:", placeholder="Ask me anything about farming...", height=100)

# # with col2:
# #     # Add spacing to center the button vertically
# #     st.markdown("<br>", unsafe_allow_html=True)
# #     st.markdown("<br>", unsafe_allow_html=True)
# #     if st.button("🎤 Start Speaking", use_container_width=True):
# #         st.info("🎙 Listening... (Speech-to-text integration goes here)")

# # # --- FOOTER ---
# # st.markdown(
# #     """
# #     <br><br>
# #     <p style="text-align:center; color:white; font-size:12px;">
# #     © 2025 Krishi Mitra — Empowering Farmers with AI
# #     </p>
# #     """,
# #     unsafe_allow_html=True
# # )
# import streamlit as st
# import os

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Krishi Mitra", layout="wide")

# # --- BACKGROUND VIDEO FUNCTION ---
# def add_bg_video(video_file):
#     if not os.path.exists(video_file):
#         st.error(f"Video file not found: {video_file}")
#         return
    
#     # Create HTML video tag
#     video_html = f"""
#         <video autoplay muted loop playsinline id="bg-video">
#             <source src="file:///{video_file}" type="video/mp4">
#         </video>
#         <style>
#         #bg-video {{
#             position: fixed;
#             right: 0;
#             bottom: 0;
#             min-width: 100%;
#             min-height: 100%;
#             z-index: -1;
#             object-fit: cover;
#         }}
#         .stApp {{
#             background: transparent !important;
#         }}
#         h1, .stTitle {{
#             color: #ffffff !important;
#             text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
#         }}
#         .stMarkdown p {{
#             color: #f0f0f0 !important;
#             text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
#         }}
#         </style>
#     """
#     st.markdown(video_html, unsafe_allow_html=True)

# # --- ADD BACKGROUND VIDEO ---
# add_bg_video("D:/OPEN_AI_API/media/video.mp4")

# # --- HEADER ---
# st.markdown(
#     """
#     <h1 style="text-align:center; color:white; font-size:50px; font-weight:bold;">
#     🌾 Krishi Mitra
#     </h1>
#     <p style="text-align:center; color:white; font-size:18px;">
#     Your AI-powered agriculture assistant — Talk or Type for Instant Advice
#     </p>
#     """,
#     unsafe_allow_html=True
# )

# # --- INPUT SECTION ---
# col1, col2 = st.columns([3, 1])

# with col1:
#     user_input = st.text_area("💬 Type your query:", placeholder="Ask me anything about farming...", height=100)

# with col2:
#     st.markdown("<br><br>", unsafe_allow_html=True)
#     if st.button("🎤 Start Speaking", use_container_width=True):
#         st.info("🎙 Listening... (Speech-to-text integration goes here)")

# # --- FOOTER ---
# st.markdown(
#     """
#     <br><br>
#     <p style="text-align:center; color:white; font-size:12px;">
#     © 2025 Krishi Mitra — Empowering Farmers with AI
#     </p>
#     """,
#     unsafe_allow_html=True
# )
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
