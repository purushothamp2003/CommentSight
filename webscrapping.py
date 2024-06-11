
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

api_key = 'AIzaSyBGmU4wRfLptG1mN0B2wlVv1QCMUADRRL8'
video_id = '4mXgiOc4PU0'

youtube = build('youtube', 'v3', developerKey=api_key)

# Function to get comments from a YouTube video
def get_comments(video_id, max_results=100):
    comments = []
    next_page_token = None

    try:
        while True:
            logging.debug("Fetching comments page")
            # Fetch comments from the YouTube API
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=next_page_token,
                maxResults=max_results,
                textFormat='plainText'
            )
            response = request.execute()
            logging.debug("Response received: %s", response)

            # Parse the response and extract comments
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
                logging.debug("Comment: %s", comment)

            # Check if there are more pages of comments
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

    except HttpError as e:
        logging.error("An HTTP error occurred: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)

    return comments

# Fetch the comments for the specified video
logging.info("Fetching comments for video ID: %s", video_id)
comments = get_comments(video_id)

# Print the list of comments
for comment in comments:
    print(comment)
