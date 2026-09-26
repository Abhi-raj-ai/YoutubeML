from utils.database import get_channel, save_channel, save_videos, get_videos, get_channel_by_name, get_comments, \
    save_comments, should_refresh_channel, should_refresh_video,should_refresh_comments,get_video, save_predictions
from utils.youtube_api import search_channel, get_channel_stats, get_recent_videos, get_video_stats, get_video_comments
from googleapiclient.errors import HttpError
from utils.intent_service import predict_comments
from utils.sentiment_service import predict_sentiments


def refresh_channel(channel_id):

    try:
        channel_from_database = get_channel(channel_id)
        if channel_from_database is not None:
            fresh_channel_stat_api = get_channel_stats(channel_id)
            channel_from_database.update(fresh_channel_stat_api)
            save_channel(channel_from_database)
            return channel_from_database

        else:
            return None

    except HttpError as error:

        print(f"YouTube API error while refreshing channel: {error}")
        return None

def refresh_videos(channel_id):

    try:
        # 1. Get all existing videos for this channel from the database
        videos_from_database = get_videos(channel_id)
        if videos_from_database is None:
            return None

        # 2. Extract video IDs
        videos_ids_from_database = []
        for video in videos_from_database:
            video_id = video["video_id"]
            videos_ids_from_database.append(video_id)
        # 3. Get fresh statistics from YouTube
        updated_videos_stat_api = get_video_stats(videos_ids_from_database)
        # 4. Store the merged videos
        updated_videos_data = []
        # 5. Match database videos with fresh API statistics
        for video in videos_from_database:
            for item in updated_videos_stat_api:
                if video["video_id"] == item["video_id"]:
                    # Copy the existing video information
                    combined_video = video.copy()
                    # Add/update fresh statistics
                    combined_video.update(item)
                    # Add complete video to the list
                    updated_videos_data.append(combined_video)
        # 6. Save updated videos to database
        save_videos(updated_videos_data)

        # 7. Return all updated videos
        return updated_videos_data

    except HttpError as error:

        print(f"YouTube API error while refreshing video: {error}")
        return None


def refresh_video(video_id):

    try:
        # 1. Get the existing video from the database
        video_info_database = get_video(video_id)

        if video_info_database is None:
            return None

        # 2. Get fresh statistics from YouTube
        updated_video_stat_api = get_video_stats([video_id])

        if not updated_video_stat_api:
            return None

        # 3. Get the statistics for this video
        updated_video = updated_video_stat_api[0]

        # 4. Combine database information with fresh statistics
        combined_video = video_info_database.copy()
        combined_video.update(updated_video)

        # 5. Save the updated video
        save_videos([combined_video])

        # 6. Return the updated video
        return combined_video

    except HttpError as error:
        print(f"YouTube API error while refreshing video: {error}")
        return None


def combine_predictions(intent_results,sentiment_results):

    joined = []

    for intent_result, sentiment_result in zip(
            intent_results,
            sentiment_results
    ):

        merged = {
            **intent_result,
            **sentiment_result
        }

        joined.append(
            merged
        )

    return joined


def process_comments(video_id):

    try:

        # =====================================================
        # CHECK WHETHER COMMENTS NEED REFRESHING
        # =====================================================

        refresh_needed = should_refresh_comments(
            video_id
        )

        # =====================================================
        # CASE 1: GET COMMENTS FROM YOUTUBE API
        # =====================================================

        if refresh_needed is True:

            comments_api = get_video_comments(
                video_id
            )

            comments = comments_api

            if comments_api is None:

                return None

            # Save fresh comments into database
            save_comments(
                comments_api
            )

            # -------------------------------------------------
            # Extract only comment text and comment id
            # -------------------------------------------------

            comment_texts = [
                comment["comment_text"]
                for comment in comments
            ]

        # =====================================================
        # CASE 2: GET COMMENTS FROM DATABASE
        # =====================================================

        else:

            comments_database = get_comments(
                video_id
            )

            comments = comments_database

            if comments_database is None:

                return None

            # -------------------------------------------------
            # Extract only comment text and comment id
            # -------------------------------------------------

            comment_texts = [
                comment["comment_text"]
                for comment in comments
            ]


        # =====================================================
        # CHECK IF THERE ARE COMMENTS
        # =====================================================

        if not comment_texts:

            return []

        # =====================================================
        # INTENT PREDICTION
        # =====================================================

        predicted_comments = predict_comments(
            comment_texts
        )

        # =====================================================
        # SENTIMENT PREDICTION
        # =====================================================

        predicted_sentiments = predict_sentiments(
            comment_texts
        )

        # =====================================================
        # COMBINE BOTH PREDICTIONS
        # =====================================================

        combined_predictions = combine_predictions(
            predicted_comments,
            predicted_sentiments
        )

        # =====================================================
        # ATTACHING COMMENT ID
        # =====================================================

        for comment, prediction in zip(comments, combined_predictions):
            prediction['comment_id'] = comment["comment_id"]
        save_predictions(combined_predictions)

        # =====================================================
        # RETURN FINAL RESULTS
        # =====================================================

        return combined_predictions

    except HttpError as error:

        print(
            f"YouTube API error while processing comments: {error}"
        )

        return None

    except Exception as error:

        import traceback

        print(
            f"Error while processing comments: {error}"
        )

        traceback.print_exc()

        return None



def process_channel(channel_name):

    try:

        # =========================================================
        # 1. CHECK IF CHANNEL ALREADY EXISTS IN DATABASE
        # =========================================================

        channel_info_database = get_channel_by_name(channel_name)

        if channel_info_database is not None:

            # Get channel ID
            channel_id_database = channel_info_database["channel_id"]


            # =====================================================
            # 2. REFRESH CHANNEL IF NEEDED
            # =====================================================

            time_differ_channel_30min = should_refresh_channel(
                channel_id_database
            )

            if time_differ_channel_30min is True:

                updated_channel_data = refresh_channel(
                    channel_id_database
                )

            else:

                updated_channel_data = get_channel(
                    channel_id_database
                )


            # =====================================================
            # 3. GET LATEST VIDEOS FROM YOUTUBE API
            # =====================================================

            video_data, video_ids_string = get_recent_videos(
                channel_id_database
            )

            if video_data is None:
                print("Could not get recent videos.")
                return updated_channel_data, [], []


            # =====================================================
            # 4. GET VIDEO STATISTICS FROM YOUTUBE API
            # =====================================================

            video_stats = get_video_stats(
                video_ids_string
            )


            # =====================================================
            # 5. COMBINE VIDEO INFORMATION + STATISTICS
            # =====================================================

            latest_videos_api = []

            for video in video_data:

                for stats in video_stats:

                    if video["video_id"] == stats["video_id"]:

                        combined_video = video.copy()

                        combined_video.update(
                            stats
                        )

                        latest_videos_api.append(
                            combined_video
                        )


            # =====================================================
            # 6. SAVE/SYNCHRONIZE LATEST VIDEOS
            # =====================================================

            save_videos(
                latest_videos_api
            )


            # =====================================================
            # 7. CHECK EACH VIDEO INDIVIDUALLY
            # =====================================================

            updated_videos_data = []

            for video in latest_videos_api:

                video_id = video["video_id"]

                print(
                    f"\nProcessing video: {video_id}"
                )

                # Check whether THIS video needs refreshing
                refresh_needed = should_refresh_video(
                    video_id
                )

                if refresh_needed is True:

                    # Refresh only this video's statistics
                    updated_video = refresh_video(
                        video_id
                    )

                    if updated_video is not None:

                        updated_videos_data.append(
                            updated_video
                        )

                else:

                    # Video is still fresh
                    database_video = get_video(
                        video_id
                    )

                    if database_video is not None:

                        updated_videos_data.append(
                            database_video
                        )

                    else:

                        updated_videos_data.append(
                            video
                        )


            # =====================================================
            # 8. PROCESS COMMENTS FOR EACH VIDEO SEPARATELY
            # =====================================================

            video_comments = {}

            for video in updated_videos_data:

                video_id = video["video_id"]

                print(
                    f"Processing comments for video: {video_id}"
                )

                comments = process_comments(
                    video_id
                )

                if comments is not None:

                    # Keep comments associated with their video
                    video_comments[video_id] = comments

                else:

                    video_comments[video_id] = []


            # =====================================================
            # 9. RETURN EVERYTHING
            # =====================================================

            return (
                updated_channel_data,
                updated_videos_data,
                video_comments
            )


        # =========================================================
        # 10. CHANNEL DOES NOT EXIST → CREATE NEW CHANNEL
        # =========================================================

        else:

            # -----------------------------------------------------
            # Search channel through YouTube API
            # -----------------------------------------------------

            new_channel_data_api = search_channel(
                channel_name
            )

            if new_channel_data_api is None:

                print("Channel not found.")

                return None, None, None


            # =====================================================
            # 11. GET CHANNEL STATISTICS
            # =====================================================

            new_channel_id = new_channel_data_api["channel_id"]

            new_channel_stat_api = get_channel_stats(
                new_channel_id
            )

            new_channel_data_api.update(
                new_channel_stat_api
            )


            # =====================================================
            # 12. SAVE CHANNEL
            # =====================================================

            save_channel(
                new_channel_data_api
            )


            # =====================================================
            # 13. GET LATEST 15 VIDEOS
            # =====================================================

            video_data, video_ids_string = get_recent_videos(
                new_channel_id
            )

            if video_data is None:

                print("Could not get recent videos.")

                return (
                    new_channel_data_api,
                    [],
                    {}
                )


            # =====================================================
            # 14. GET VIDEO STATISTICS
            # =====================================================

            video_stats = get_video_stats(
                video_ids_string
            )


            # =====================================================
            # 15. COMBINE VIDEO INFORMATION + STATISTICS
            # =====================================================

            new_combined_videos_api = []

            for video in video_data:

                for stats in video_stats:

                    if video["video_id"] == stats["video_id"]:

                        combined_video = video.copy()

                        combined_video.update(
                            stats
                        )

                        new_combined_videos_api.append(
                            combined_video
                        )


            # =====================================================
            # 16. SAVE VIDEOS
            # =====================================================

            save_videos(
                new_combined_videos_api
            )


            # =====================================================
            # 17. PROCESS COMMENTS FOR EACH VIDEO SEPARATELY
            # =====================================================

            video_comments = {}

            for video in new_combined_videos_api:

                video_id = video["video_id"]

                print(
                    f"\nProcessing comments for video: {video_id}"
                )

                comments = process_comments(
                    video_id
                )

                if comments is not None:

                    # Keep comments associated with their video
                    video_comments[video_id] = comments

                else:

                    video_comments[video_id] = []


            # =====================================================
            # 18. RETURN NEW CHANNEL DATA
            # =====================================================

            return (
                new_channel_data_api,
                new_combined_videos_api,
                video_comments
            )


    # =============================================================
    # HANDLE YOUTUBE API ERRORS
    # =============================================================

    except HttpError as error:

        print(
            f"YouTube API error while processing channel: {error}"
        )

        return None, None, None



def get_video_list(videos):

    video_list = []

    for video in videos:

        data = {
            "video_id": video["video_id"],
            "title": video["title"]
        }

        video_list.append(data)

    return video_list


def get_video_analytics_data(channel_name):

    channel_data = search_channel(channel_name)

    if channel_data:
        extracted_channel_data = {
            "channel_id": channel_data["channel_id"],
            "channel_name": channel_data["channel_name"],
            "channel_description": channel_data["channel_description"],
            "publish_date": channel_data["published_date"],
        }

        channel_id = extracted_channel_data["channel_id"]

        video_datas, video_ids_string = get_recent_videos(channel_id)
        videos_stats = get_video_stats(video_ids_string)

        extracted_videos_data = []

        for video_data in video_datas:
            video_id = video_data["video_id"]

            for video_stats in videos_stats:

                if video_stats["video_id"] == video_id:

                    videos_data = {
                        "channel_id": video_data["channel_id"],
                        "video_id": video_id,
                        "title": video_data["title"],
                        "description": video_data["description"],
                        "published_date": video_data["published_date"],
                        "view_count": video_stats["view_count"],
                        "like_count": video_stats["like_count"],
                        "comment_count": video_stats["comment_count"],
                    }

                    extracted_videos_data.append(videos_data)

        return extracted_channel_data, extracted_videos_data

    else:
        return None


