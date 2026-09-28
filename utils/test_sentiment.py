# from utils.channel_service import get_or_fetch_comments
# from utils.sentiment_service import predict_sentiments
#
#
# video_id = "QTiqaxc-QEo"
#
#
# # Step 1: Get comments
# comments_data = get_or_fetch_comments(video_id)
#
#
# # Step 2: Check whether comments exist
# if comments_data:
#
#     # Step 3: Send complete comment dictionaries
#     # to the sentiment model
#     sentiment_results = predict_sentiments(
#         comments_data
#     )
#
#     # Step 4: Number of comments
#     print(
#         "Number of comments:",
#         len(comments_data)
#     )
#
#     # Step 5: Number of predictions
#     print(
#         "Number of predictions:",
#         len(sentiment_results)
#     )
#
#     # Step 6: Display first 10 predictions
#     print("\nFirst 10 predictions:\n")
#
#     for result in sentiment_results[:10]:
#         print(result)
#
# else:
#
#     print("No comments found.")
#
#
from utils.channel_service import process_comments

result = process_comments("QTiqaxc-QEo")

print("Number of combined predictions:", len(result))

for prediction in result[:5]:
    print(prediction)