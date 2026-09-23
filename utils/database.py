from pathlib import Path
import sqlite3
import time
from datetime import datetime, timedelta

import pandas

from utils.youtube_api import get_video_stats, youtube, get_video_comment_count

# Get the script's directory
current_folder = Path(__file__).resolve().parent

# Go up one level
BASE_DIR = current_folder.parent

# Database path
DATABASE_PATH = BASE_DIR / "database" / "youtube.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    with open(BASE_DIR / "database" / "schema.sql", "r") as file:
        schema = file.read()

    cursor.executescript(schema)
    connection.commit()
    connection.close()



def data_temp():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM comments')
    res =cursor.fetchall()
    print(res)

    connection.close()


def save_channel(channel):
    connection = get_connection()
    cursor = connection.cursor()

    current_time = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime()
    )

    cursor.execute("""
        INSERT INTO channels (
            channel_id,
            channel_name,
            description,
            publish_date,
            subscriber_count,
            view_count,
            video_count,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT (channel_id)
        DO UPDATE SET
            channel_name = excluded.channel_name,
            description = excluded.description,
            subscriber_count = excluded.subscriber_count,
            view_count = excluded.view_count,
            video_count = excluded.video_count,
            last_updated = excluded.last_updated
    """, (
        channel["channel_id"],
        channel["channel_name"],
        channel["channel_description"],
        channel["published_date"],
        channel["subscriber_count"],
        channel["view_count"],
        channel["video_count"],
        current_time
    ))

    connection.commit()
    connection.close()



def get_channel(channel_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""SELECT * FROM channels
                    WHERE channel_id = ?""",(channel_id,))


    channel_info = cursor.fetchone()


    if channel_info != None:

        channel_info_dict = {
            "channel_id": channel_info[0],
            "channel_name": channel_info[1],
            "channel_description": channel_info[2],
            "published_date": channel_info[3],
            "subscriber_count": channel_info[4],
            "view_count": channel_info[5],
            "video_count": channel_info[6],
            "last_updated": channel_info[7]
        }
        connection.close()
        return channel_info_dict
    else:
        connection.close()
        return None



def save_videos(videos):
    connection = get_connection()
    cursor = connection.cursor()

    current_time = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime()
    )

    data = [
        (video["video_id"],
        video["channel_id"],
        video["title"],
        video["description"],
        video["published_date"],
        video["view_count"],
        video["like_count"],
        video["comment_count"],
        current_time)
        for video in videos
    ]

    cursor.executemany("""
    INSERT INTO videos (
    video_id,
    channel_id,
    title,
    description,
    publish_date,
    view_count,
    like_count,
    comment_count,
    last_updated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT (video_id)
    DO UPDATE SET
         title = excluded.title,
         description = excluded.description,
         view_count = excluded.view_count,
         like_count = excluded.like_count,
         comment_count = excluded.comment_count,
         last_updated = excluded.last_updated
     """, data )

    connection.commit()
    connection.close()


def get_video(video_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM videos
        WHERE video_id = ?
    """, (video_id,))

    video = cursor.fetchone()

    connection.close()

    if video is not None:
        video_info = {
            "channel_id": video[0],
            "video_id": video[1],
            "title": video[2],
            "description": video[3],
            "published_date": video[4],
            "view_count": video[5],
            "like_count": video[6],
            "comment_count": video[7],
            "last_updated": video[8]
        }

        return video_info

    return None


def should_refresh_channel(channel_id):
    channel_info = get_channel(channel_id)
    last_updated_time = datetime.strptime(
        channel_info["last_updated"],
        "%Y-%m-%d %H:%M:%S"
    )
    current_time = datetime.now()
    time_difference = current_time - last_updated_time

    if time_difference >= timedelta(minutes=30):
        return True
    else:
        return False


def should_refresh_video(video_id):

    video_info = get_video(video_id)

    if video_info is None:
        return False

    if video_info["last_updated"] is None:
        return True

    last_updated_time = datetime.strptime(
        video_info["last_updated"],
        "%Y-%m-%d %H:%M:%S"
    )

    current_time = datetime.now()

    time_difference = current_time - last_updated_time

    if time_difference >= timedelta(minutes=30):
        return True

    return False



def get_videos(channel_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(""" SELECT * FROM videos
                   WHERE channel_id = ? """, (channel_id,))

    videos_info = cursor.fetchall()

    videos_info_dict = []
    for video in videos_info:
            video_info = {
                "channel_id": video[0],
                "video_id": video[1],
                "title": video[2],
                "description": video[3],
                "published_date": video[4],
                "view_count": video[5],
                "like_count": video[6],
                "comment_count": video[7],
                "last_updated": video[8]
            }
            videos_info_dict.append(video_info)
    connection.close()

    if videos_info:
        return videos_info_dict

    else:
        return None



def get_channel_by_name(channel_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(""" SELECT * FROM channels
    WHERE channel_name = ? """, (channel_name,))

    channel_info = cursor.fetchone()

    if channel_info != None:

        channel_info_dict = {
            "channel_id": channel_info[0],
            "channel_name": channel_info[1],
            "channel_description": channel_info[2],
            "published_date": channel_info[3],
            "subscriber_count": channel_info[4],
            "view_count": channel_info[5],
            "video_count": channel_info[6],
            "last_updated": channel_info[7]
        }
        connection.close()
        return channel_info_dict
    else:
        connection.close()
        return None


def save_comments(comments):
    connection = get_connection()
    cursor = connection.cursor()

    data = [
        (
            comment["comment_id"],
            comment["video_id"],
            comment["comment_text"],
            comment["author"],
            comment["publish_date"],
            comment["like_count"]
        )
        for comment in comments
    ]

    cursor.executemany("""INSERT INTO comments (
    comment_id,
    video_id,
    comment_text,
    author,
    publish_date,
    like_count
    ) Values (?, ?, ?, ?, ?, ?)

    ON CONFLICT (comment_id)
    DO UPDATE SET
           comment_text = excluded.comment_text,
           author = excluded.author,
           like_count = excluded.like_count""", data)

    connection.commit()
    connection.close()


def get_comments(video_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
           SELECT *
           FROM comments
           WHERE video_id = ?
           ORDER BY publish_date DESC
           LIMIT 1000
       """, (video_id,))

    comments_info = cursor.fetchall()
    comments_info_dict = []
    for comment in comments_info:
        comments_data = {
            "comment_id":comment[0],
            "video_id":comment[1],
            "comment_text":comment[2],
            "author":comment[3],
            "published_date":comment[4],
            "like_count":comment[5],
        }
        comments_info_dict.append(comments_data)
    connection.close()

    if comments_info_dict:
        return comments_info_dict
    else:
        return None


def should_refresh_comments(video_id):
    # Get comments currently stored in database
    comments_info = get_comments(video_id)

    if comments_info is not None:
        database_comment_count = len(comments_info)
    else:
        database_comment_count = 0

    youtube_comment_count = get_video_comment_count(video_id)

    # Calculate how many comments are missing from database
    new_comment_count = youtube_comment_count - database_comment_count

    # Refresh only when 100 or more new comments exist
    if new_comment_count >= 100:
        return True
    else:
        return False


def save_predictions(predictions):
    connection = get_connection()
    cursor = connection.cursor()

    data = [
        (
        prediction['comment_id'],
        prediction['Intent'],
        float(prediction['Intent_Confidence']),
        prediction['Final_Intent'],
        prediction['Sentiment'],
        float(prediction['Sentiment_Confidence'])
        )
        for prediction in predictions
    ]

    cursor.executemany("""INSERT INTO predictions (
    
    comment_id,
    intent,
    intent_confidence,
    final_intent,
    sentiment,
    sentiment_confidence) 
    VALUES (?, ?, ?, ?, ?, ?)
    
    ON CONFLICT (comment_id)
    DO UPDATE SET 
            intent = excluded.intent,
            intent_confidence = excluded.intent_confidence,
            final_intent = excluded.final_intent,
            sentiment = excluded.sentiment,
            sentiment_confidence = excluded.sentiment_confidence
    """, data)

    connection.commit()
    connection.close()


def get_predictions(comment_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(""" 
                SELECT comment_text,
                       final_intent,
                       sentiment,
                       intent_confidence,
                       sentiment_confidence
                FROM comments
                INNER JOIN predictions
                ON predictions.comment_id = comments.comment_id
                WHERE comments.comment_id = ? 
                       """, (comment_id,))

    comments_info = cursor.fetchall()
    connection.close()
    return comments_info


def get_video_predictions(video_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
              SELECT comment_text,
                     final_intent,
                     sentiment,
                     intent_confidence,
                     sentiment_confidence
              FROM comments
              INNER JOIN predictions
              ON predictions.comment_id = comments.comment_id
              WHERE comments.video_id = ? 
              """,
                   (video_id,))
    comments_info = cursor.fetchall()
    comments_info_dataframe = pandas.DataFrame(
        comments_info,
        columns=['comment_text', 'final_intent', 'sentiment', 'intent_confidence', 'sentiment_confidence']
                                               )
    connection.close()
    return comments_info_dataframe

def get_intent_analysis(video_id):
    df = get_video_predictions(video_id)

    ### Value counts
    intent_counts= df['final_intent'].value_counts()
    intent_percentage = df['final_intent'].value_counts(normalize=True) * 100

    return intent_counts, intent_percentage

def get_sentiment_analysis(video_id):
    df = get_video_predictions(video_id)

    ### Value counts
    sentiment_counts= df['sentiment'].value_counts()
    sentiment_percentage = df['sentiment'].value_counts(normalize=True) * 100

    return sentiment_counts, sentiment_percentage


def get_video_analytics(video_id):
    intent_analysis = get_intent_analysis(video_id)
    sentiment_analysis = get_sentiment_analysis(video_id)

    data = {
        "intent_counts": intent_analysis[0],
        "intent_percentage": intent_analysis[1],
        "sentiment_counts": sentiment_analysis[0],
        "sentiment_percentage": sentiment_analysis[1]
    }

    return data

# if __name__ == "__main__":
#     result = get_video_analytics('xHdoc_JRYK0')
#     print(result)
