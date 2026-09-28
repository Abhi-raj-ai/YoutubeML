import streamlit as st
import pandas as pd

from utils.youtube_api import (
    search_channel,
    get_recent_videos
)

from utils.database import (
    get_video_analytics,
    get_video_predictions
)

from utils.channel_service import (
    process_comments
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Comment Analysis",
    page_icon="💬",
    layout="wide"
)


# --------------------------------------------------
# Page title
# --------------------------------------------------

st.title("💬 Comment Analysis")

st.markdown(
    "Analyze viewer intent and sentiment from YouTube comments."
)


# --------------------------------------------------
# Channel input
# --------------------------------------------------

channel_name = st.text_input(
    "Enter YouTube channel name",
    placeholder="e.g. MrBeast"
)


# --------------------------------------------------
# Analyze channel
# --------------------------------------------------

if st.button("🔍 Load Videos"):

    if channel_name.strip() == "":

        st.warning(
            "Please enter a channel name."
        )

    else:

        with st.spinner(
            "Finding channel..."
        ):

            channel_data = search_channel(
                channel_name
            )

        if not channel_data:

            st.error(
                "Channel not found. "
                "Please check the channel name."
            )

        else:

            channel_id = channel_data[
                "channel_id"
            ]

            with st.spinner(
                "Loading recent videos..."
            ):

                videos_data, video_ids_string = (
                    get_recent_videos(
                        channel_id
                    )
                )

            if not videos_data:

                st.info(
                    "No videos found."
                )

            else:

                # Store videos in session state
                st.session_state[
                    "videos_data"
                ] = videos_data

                st.success(
                    f"Found {len(videos_data)} recent videos."
                )


# --------------------------------------------------
# Video selection
# --------------------------------------------------

if "videos_data" in st.session_state:

    videos_data = st.session_state[
        "videos_data"
    ]

    st.divider()

    st.subheader(
        "🎬 Select a Video"
    )

    video_options = {}

    for video in videos_data:

        video_options[
            video["title"]
        ] = video["video_id"]

    selected_video_title = st.selectbox(
        "Choose a video",
        list(video_options.keys())
    )

    selected_video_id = video_options[
        selected_video_title
    ]

    # --------------------------------------------------
    # Video information
    # --------------------------------------------------

    thumbnail_url = (
        f"https://img.youtube.com/vi/"
        f"{selected_video_id}/maxresdefault.jpg"
    )

    video_url = (
        f"https://www.youtube.com/watch?v="
        f"{selected_video_id}"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.image(
            thumbnail_url,
            width="stretch"
        )

    with col2:

        st.subheader(
            selected_video_title
        )

        st.markdown(
            f"[▶ Watch on YouTube]({video_url})"
        )

        st.caption(
            f"Video ID: {selected_video_id}"
        )

    st.divider()

    # --------------------------------------------------
    # Check existing predictions
    # --------------------------------------------------

    predictions = get_video_predictions(
        selected_video_id
    )

    # --------------------------------------------------
    # Process comments button
    # --------------------------------------------------

    if predictions.empty:

        st.info(
            "This video has not been analyzed yet."
        )

        if st.button(
            "🤖 Analyze Comments"
        ):

            with st.spinner(
                "Fetching comments and running NLP models..."
            ):

                combined_predictions = (
                    process_comments(
                        selected_video_id
                    )
                )

            if combined_predictions:

                st.success(
                    f"Successfully analyzed "
                    f"{len(combined_predictions)} comments."
                )

                # Refresh Streamlit
                st.rerun()

            else:

                st.warning(
                    "No comments were found for this video."
                )

    else:

        st.success(
            f"{len(predictions)} comments "
            "have already been analyzed."
        )


# --------------------------------------------------
# Display analytics
# --------------------------------------------------

if "videos_data" in st.session_state:

    predictions = get_video_predictions(
        selected_video_id
    )

    if not predictions.empty:

        # --------------------------------------------------
        # Get analytics
        # --------------------------------------------------

        analytics = get_video_analytics(
            selected_video_id
        )

        intent_counts = analytics[
            "intent_counts"
        ]

        intent_percentage = analytics[
            "intent_percentage"
        ]

        sentiment_counts = analytics[
            "sentiment_counts"
        ]

        sentiment_percentage = analytics[
            "sentiment_percentage"
        ]

        # --------------------------------------------------
        # Overview
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "📊 Comment Overview"
        )

        total_comments = len(
            predictions
        )

        positive_count = sentiment_counts.get(
            "Positive",
            0
        )

        negative_count = sentiment_counts.get(
            "Negative",
            0
        )

        col1, col2, col3 = st.columns(
            3
        )

        with col1:

            st.metric(
                "Analyzed Comments",
                total_comments
            )

        with col2:

            st.metric(
                "Positive",
                int(positive_count)
            )

        with col3:

            st.metric(
                "Negative",
                int(negative_count)
            )

        # --------------------------------------------------
        # Intent analysis
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "🎯 Viewer Intent"
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.write(
                "### Intent Distribution"
            )

            intent_chart_data = pd.DataFrame(
                {
                    "Intent": intent_counts.index,
                    "Comments": intent_counts.values
                }
            )

            st.bar_chart(
                intent_chart_data.set_index(
                    "Intent"
                )
            )

        with col2:

            st.write(
                "### Intent Percentage"
            )

            intent_percentage_data = (
                intent_percentage
                .round(2)
                .to_frame(
                    "Percentage"
                )
            )

            st.dataframe(
                intent_percentage_data,
                width="stretch"
            )

        # --------------------------------------------------
        # Sentiment analysis
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "😊 Sentiment Analysis"
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.write(
                "### Sentiment Distribution"
            )

            sentiment_chart_data = pd.DataFrame(
                {
                    "Sentiment": sentiment_counts.index,
                    "Comments": sentiment_counts.values
                }
            )

            st.bar_chart(
                sentiment_chart_data.set_index(
                    "Sentiment"
                )
            )

        with col2:

            st.write(
                "### Sentiment Percentage"
            )

            sentiment_percentage_data = (
                sentiment_percentage
                .round(2)
                .to_frame(
                    "Percentage"
                )
            )

            st.dataframe(
                sentiment_percentage_data,
                width="stretch"
            )

        # --------------------------------------------------
        # Individual predictions
        # --------------------------------------------------

        # --------------------------------------------------
        # Individual comment predictions
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "💬 Comment Predictions"
        )

        display_df = predictions.copy()

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            intent_options = [
                                 "All"
                             ] + sorted(
                display_df["final_intent"].dropna().unique().tolist()
            )

            selected_intent = st.selectbox(
                "🎯 Filter by Intent",
                intent_options
            )

        with col2:

            sentiment_options = [
                                    "All"
                                ] + sorted(
                display_df["sentiment"].dropna().unique().tolist()
            )

            selected_sentiment = st.selectbox(
                "😊 Filter by Sentiment",
                sentiment_options
            )

        with col3:

            min_confidence = st.slider(
                "🎯 Minimum Intent Confidence",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )

        # --------------------------------------------------
        # Apply filters
        # --------------------------------------------------

        filtered_df = display_df.copy()

        # Intent filter

        if selected_intent != "All":
            filtered_df = filtered_df[
                filtered_df["final_intent"]
                == selected_intent
                ]

        # Sentiment filter

        if selected_sentiment != "All":
            filtered_df = filtered_df[
                filtered_df["sentiment"]
                == selected_sentiment
                ]

        # Confidence filter

        filtered_df = filtered_df[
            filtered_df["intent_confidence"]
            >= min_confidence
            ]

        # --------------------------------------------------
        # Filter result count
        # --------------------------------------------------

        st.write(
            f"Showing **{len(filtered_df)}** "
            f"of **{len(display_df)}** comments"
        )

        # --------------------------------------------------
        # Prepare table for display
        # --------------------------------------------------

        filtered_df = filtered_df.rename(
            columns={
                "comment_text": "Comment",
                "final_intent": "Intent",
                "sentiment": "Sentiment",
                "intent_confidence":
                    "Intent Confidence",
                "sentiment_confidence":
                    "Sentiment Confidence"
            }
        )

        # --------------------------------------------------
        # Round confidence values
        # --------------------------------------------------

        if "Intent Confidence" in filtered_df.columns:
            filtered_df[
                "Intent Confidence"
            ] = filtered_df[
                "Intent Confidence"
            ].round(2)

        if "Sentiment Confidence" in filtered_df.columns:
            filtered_df[
                "Sentiment Confidence"
            ] = filtered_df[
                "Sentiment Confidence"
            ].round(2)

        # --------------------------------------------------
        # Display filtered comments
        # --------------------------------------------------

        # --------------------------------------------------
        # Display comments with multiline text
        # --------------------------------------------------

        if filtered_df.empty:

            st.info("No comments match the selected filters.")

        else:

            for index, row in filtered_df.iterrows():
                comment = row["Comment"]
                intent = row["Intent"]
                sentiment = row["Sentiment"]
                intent_confidence = row["Intent Confidence"]
                sentiment_confidence = row["Sentiment Confidence"]

                with st.container(border=True):
                    st.markdown(
                        f"**💬 Comment**  \n"
                        f"{comment}"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.markdown(
                            f"**🎯 Intent:** {intent}"
                        )

                    with col2:
                        st.markdown(
                            f"**😊 Sentiment:** {sentiment}"
                        )

                    with col3:
                        st.markdown(
                            f"**Intent Confidence:** "
                            f"{intent_confidence:.2f}%"
                        )

                    with col4:
                        st.markdown(
                            f"**Sentiment Confidence:** "
                            f"{sentiment_confidence:.2f}%"
                        )