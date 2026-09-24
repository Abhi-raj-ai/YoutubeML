import streamlit as st

from utils.channel_service import process_channel

def format_number(number):
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"

    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"

    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"

    else:
        return str(number)


st.set_page_config(
    page_title="YoutubeML Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("📊 YouTube Channel Dashboard")

st.markdown(
    "Analyze a YouTube channel and explore its latest videos."
)


channel_name = st.text_input(
    "Enter YouTube channel name",
    placeholder="e.g. MrBeast"
)


if st.button("🔍 Analyze Channel"):

    if channel_name.strip() == "":
        st.warning("Please enter a channel name.")

    else:

        with st.spinner("Analyzing channel..."):

            channel_data, videos_data, video_comments = process_channel(
                channel_name
            )

        if channel_data is not None:

            st.success("Channel analyzed successfully!")

            st.subheader("📺 Channel Information")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Subscribers",
                    format_number(channel_data["subscriber_count"])
                )

            with col2:
                st.metric(
                    "Total Views",
                    format_number(channel_data["view_count"])
                )

            with col3:
                st.metric(
                    "Videos",
                    format_number(channel_data["video_count"])
                )

            with col4:
                st.metric(
                    "Channel",
                    channel_data["channel_name"]
                )
                
            st.divider()

            st.subheader("📝 Channel Description")

            st.write(
                channel_data.get(
                    "description",
                    "No description available."
                )
            )

            st.divider()

            st.subheader("🎬 Latest Videos")

            if videos_data:

                for index, video in enumerate(videos_data, start=1):
                    video_id = video["video_id"]
                    video_title = video["title"]

                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    thumbnail_url = (
                        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    )

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.image(
                            thumbnail_url,
                            width="stretch"
                        )

                    with col2:
                        st.write(f"### {index}. {video_title}")

                        st.markdown(
                            f"[▶️ Watch Video]({video_url})"
                        )

                        st.caption(
                            f"Video ID: {video_id}"
                        )

                    st.divider()

            else:

                st.info("No videos found.")
        else:

            st.error(
                "Unable to process the channel. "
                "Please check the channel name and try again."
            )