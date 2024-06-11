
from flask import Flask, request, render_template, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

api_key = 'AIzaSyBGmU4wRfLptG1mN0B2wlVv1QCMUADRRL8'

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET'])
def results():
    url = request.args.get('url')
    # Extract the video ID from the URL
    video_id = extract_video_id(url)
    if video_id:
        comments = get_comments(video_id)
        return jsonify(comments)
    else:
        return jsonify({'error': 'Invalid URL'}), 400


from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path.lstrip('/')
    else:
        query = parsed_url.query
        params = parse_qs(query)
        return params.get('v', [None])[0]

if __name__ == '__main__':
    app.run(debug=True)
