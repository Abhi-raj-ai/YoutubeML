import streamlit as st

from utils.channel_service import get_video_analytics_data


st.set_page_config(
    page_title="Video Analytics",
    page_icon="📈",
    layout="wide"
)


def format_number(number):

    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"

    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"

    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"

    else:
        return str(number)


st.title("📈 Video Analytics")

st.markdown(
    "Analyze the latest videos of a YouTube channel."
)


channel_name = st.text_input(
    "Enter YouTube channel name",
    placeholder="e.g. MrBeast"
)


if st.button("🔍 Analyze Videos"):

    if channel_name.strip() == "":
        st.warning("Please enter a channel name.")

    else:

        with st.spinner("Fetching latest videos..."):

            channel_data, videos_data = get_video_analytics_data(
                channel_name
            )

        if channel_data is not None:

            st.success(
                f"Showing latest videos from {channel_data['channel_name']}"
            )

            st.divider()

            if videos_data:

                for index, video in enumerate(videos_data, start=1):

                    video_id = video["video_id"]

                    video_url = (
                        f"https://www.youtube.com/watch?v={video_id}"
                    )

                    thumbnail_url = (
                        f"https://img.youtube.com/vi/"
                        f"{video_id}/maxresdefault.jpg"
                    )

                    st.subheader(
                        f"{index}. {video['title']}"
                    )

                    col1, col2 = st.columns([1, 2])

                    with col1:

                        st.image(
                            thumbnail_url,
                            width="stretch"
                        )

                        st.markdown(
                            f"[▶ Watch Video]({video_url})"
                        )

                    with col2:

                        metric1, metric2, metric3 = st.columns(3)

                        with metric1:
                            st.metric(
                                "Views",
                                format_number(
                                    video["view_count"]
                                )
                            )

                        with metric2:
                            st.metric(
                                "Likes",
                                format_number(
                                    video["like_count"]
                                )
                            )

                        with metric3:
                            st.metric(
                                "Comments",
                                format_number(
                                    video["comment_count"]
                                )
                            )

                        st.write(
                            "**Uploaded:**",
                            video["published_date"]
                        )

                        st.write(
                            "**Video ID:**",
                            video_id
                        )

                    st.divider()

            else:

                st.info("No videos found.")

        else:

            st.error(
                "Unable to process the channel. "
                "Please check the channel name and try again."
            )