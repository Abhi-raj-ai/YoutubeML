import streamlit as st

from utils.channel_service import process_channel


st.title("YouTube Channel Analyzer - Youtube ML")


channel_name = st.text_input(
    "Enter YouTube channel name",
    placeholder="e.g. Mr beast"
)


if st.button("Analyze"):

    if channel_name.strip() == "":
        st.warning("Please enter a channel name.")

    else:

        channel_data, videos_data, video_comments = process_channel(
            channel_name
        )

        if channel_data is not None:

            st.success("Channel found!")

            st.subheader("Channel Information")

            st.write(channel_data)

            st.subheader("Videos")

            st.write(videos_data)

        else:

            st.error("Unable to process channel.")