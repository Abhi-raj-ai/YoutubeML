CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT,
    description TEXT,
    publish_date TEXT,
    subscriber_count INTEGER,
    view_count INTEGER,
    video_count INTEGER,
    last_updated TEXT
);


CREATE TABLE IF NOT EXISTS videos (
    channel_id TEXT,
    video_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    publish_date TEXT,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    last_updated TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
    );


CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    video_id TEXT,
    comment_text TEXT,
    author TEXT,
    publish_date TEXT,
    like_count INTEGER,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE IF NOT EXISTS predictions (
    comment_id TEXT PRIMARY KEY,
    intent TEXT,
    intent_confidence REAL,
    final_intent TEXT,
    sentiment TEXT,
    sentiment_confidence REAL,
    FOREIGN KEY (comment_id) REFERENCES comments(comment_id)
)