from googleapiclient.discovery import build
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(filename='.env'))

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)


##### Search channel

def search_channel(channel_name):
    request = youtube.search().list(
        part="snippet",
        maxResults=2,
        q=channel_name,
        type="channel",
    )
    response = request.execute()

    ## dictionary.get(key, default_value) .get give None otherwise it give key error

    data = response.get("items",[])
    if data:
        channel_id = data[0]["id"]["channelId"]
        actual_channel_name = data[0]["snippet"]["title"]
        description = data[0]["snippet"]["description"]
        published_date = data[0]["snippet"]["publishedAt"]

        return {
            "channel_id": channel_id,
            "channel_name": actual_channel_name,
            "channel_description": description,
            "published_date": published_date
        }


    else:
        return None



###### Channel stat for youtube_api

def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    data = response.get('items',[])

    if data:
        subscriber_count = int(data[0]["statistics"]["subscriberCount"])
        view_count = int(data[0]["statistics"]["viewCount"])
        video_count = int(data[0]["statistics"]["videoCount"])

        return {
            "subscriber_count": subscriber_count,
            "view_count": view_count,
            "video_count": video_count
        }
    else:
        return None




#### Getting 15 recent videos
def get_recent_videos(channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=15,
        type='video',
        order="date",
    )

    response = request.execute()
    items = response.get("items", [])

    video_data = []
    for item in items:
        video_ids = item["id"]["videoId"]
        channel_ids = item["snippet"]["channelId"]
        titles = item["snippet"]["title"]
        descriptions = item["snippet"]["description"]
        published_dates = item["snippet"]["publishedAt"]

        video_data.append({
            "video_id": video_ids,
            "channel_id": channel_ids,
            "title": titles,
            "description": descriptions,
            "published_date": published_dates
        })

    video_ids = [video_id["video_id"] for video_id in video_data]
    video_ids_string = ",".join(video_ids)
    return [video_data, video_ids_string]



#### Getting video states like comments and like
def get_video_stats(video_ids_string):
    request = youtube.videos().list(part='statistics', id=video_ids_string)
    response = request.execute()

    video_stats_response = response["items"]

    video_stats = []
    for item in video_stats_response:
        video_id = item['id']
        view_count = int(item['statistics']['viewCount'])
        like_count = int(item['statistics']['likeCount'])
        comment_count = int(item['statistics']['commentCount'])

        video_stats.append({
            'video_id': video_id,
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count
        })

    return video_stats

def get_video_comments(video_id,max_comments=1000):

    comments_stats = []

    page_token = None

    while True:

        # First request has pageToken=None.
        # Later requests use the token received from YouTube.
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            order='time',
            textFormat='plainText',
            pageToken=page_token
        )

        response = request.execute()

        comments_response = response.get("items", [])

        # Extract comments from the current page
        for comment in comments_response:

            comment_id = comment['snippet']['topLevelComment']['id']

            comment_video_id = comment['snippet']['videoId']

            comment_text = comment['snippet']['topLevelComment']['snippet']['textOriginal']

            author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']

            published_date = comment['snippet']['topLevelComment']['snippet']['publishedAt']

            like_count = int(
                comment['snippet']['topLevelComment']['snippet']['likeCount']
            )

            comments_stats.append({
                'comment_id': comment_id,
                'video_id': comment_video_id,
                'comment_text': comment_text,
                'author': author,
                'publish_date': published_date,
                'like_count': like_count
            })

            # Stop after collecting max comments
            if len(comments_stats) >= max_comments:
                return comments_stats

        # Get token for the next page
        page_token = response.get('nextPageToken')

        # No more pages
        if page_token is None:
            break

    return comments_stats




def get_video_comment_count(video_id):
    request = youtube.videos().list(part='statistics', id=video_id)
    response = request.execute()
    comment_count = int(response['items'][0]['statistics']['commentCount'])
    return comment_count



