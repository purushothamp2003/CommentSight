from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from config import API_KEY

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(video_id, max_results=100):
    comments = []
    next_page_token = None

    try:
        while True:
            logging.debug("Fetching comments page")
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=next_page_token,
                maxResults=max_results,
                textFormat='plainText'
            )
            response = request.execute()
            logging.debug("Response received: %s", response)

            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
                logging.debug("Comment: %s", comment)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

    except HttpError as e:
        logging.error("An HTTP error occurred: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)

    return comments
