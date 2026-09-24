import streamlit as st


st.set_page_config(
    page_title="YoutubeML",
    page_icon="🎬",
    layout="wide"
)


st.title("🎬 YoutubeML")

st.subheader("YouTube Analytics & NLP Platform")

st.write(
    """
    YoutubeML analyzes YouTube channels, videos, and audience comments
    using machine learning and natural language processing.
    """
)

st.divider()

st.subheader("🚀 Available Features")

st.markdown(
    """
    ### 📊 Dashboard
    Explore channel information and latest videos.

    ### 📈 Video Analytics
    Analyze video performance, audience intent, and sentiment.

    ### 💬 Comment Analysis
    Understand what viewers are saying.

    ### 🤖 Comment Predictions
    Explore individual NLP predictions from the trained models.
    """
)

st.info(
    "Use the sidebar to navigate between the different sections."
)