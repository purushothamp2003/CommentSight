
from flask import Flask, request, render_template, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from wordcloud import WordCloud,STOPWORDS
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import re
import emoji
from langdetect import detect
from transformers import pipeline


nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')

wnl = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()
stop_words = stopwords.words('english')

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

# def clean(org_comments):
#     y = []
#     for x in org_comments:
#         x = x.split()
#         x = [i.lower().strip() for i in x]
#         x = [i for i in x if i not in stop_words]
#         x = [i for i in x if len(i)>2]
#         x = [wnl.lemmatize(i) for i in x]
#         y.append(' '.join(x))
#     return y

def map_comments_to_labels(clean_comments, sentiment_analysis_output):
  """
  Maps each comment to its corresponding sentiment label.

  Args:
      clean_comments: A list of cleaned comments (strings).
      sentiment_analysis_output: A list of dictionaries from the sentiment analysis model,
                                  containing "label" and "score" keys for each comment.

  Returns:
      A list of tuples, where each tuple contains the original comment (string)
      and its corresponding sentiment label (string).
  """

  # Check if list lengths match to avoid index errors
  if len(clean_comments) != len(sentiment_analysis_output):
    raise ValueError("Lengths of comments and sentiment analysis output don't match!")

  comment_label_pairs = []
  for i in range(len(clean_comments)):
    comment = clean_comments[i]
    sentiment_dict = sentiment_analysis_output[i]
    label = sentiment_dict["label"]
    comment_label_pairs.append((comment, label))

  return comment_label_pairs


def clean_comment(comment):
  comment = comment.lower()  # Lowercase
  comment = re.sub(r'[^\w\s]', '', comment)  # Remove punctuation
  comment = emoji.demojize(comment, delimiters="_")  # Convert emojis to text descriptions
  comment = re.sub(r'\s\s+', ' ', comment)  # Remove extra whitespace
  # Optionally remove or replace URLs here (see comments above)
  return comment


def clean_comments(comments):
  cleaned_comments = []
  for comment in comments:
    cleaned_comment = clean_comment(comment)
    try:
      # Detect language using langdetect
      if detect(cleaned_comment) == 'en':  # Check if language is English
        cleaned_comments.append(cleaned_comment)
    except:
      pass  # Ignore exceptions from langdetect (e.g., low confidence)
  return cleaned_comments


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
    else:
        return jsonify({'error': 'Invalid URL'}), 400
    

    n = len(comments)

    if n < 200 :
        comments = comments[:]
    else:
        comments = comments[:200]


    clean_commentso = clean_comments(comments)

    sentiment_model = pipeline(model="Purushotham2003/finetuning-sentiment-model-3000-samples")

    clean_commentso1 = sentiment_model(clean_commentso)

    clean_commentso12 = map_comments_to_labels(clean_commentso , clean_commentso1)
 
    predictions = []

    scores = []

    np,nn,nne = 0,0,0



    

    for sentiment_dict in clean_commentso1:
        label = sentiment_dict["label"]  # Access label using dictionary key
        score = sentiment_dict["score"]  # Access score using dictionary key
        scores.append(score)

        if label == 'LABEL_0':
            predictions.append('POSITIVE')
            np += 1
        elif label == 'LABEL_1':
            predictions.append('NEGATIVE')
            nn += 1
        else:
            predictions.append('NEUTRAL')
            nne += 1

    dic = []

    for i,cc in enumerate(clean_commentso):
        x={}
        x['sent'] = predictions[i]
        x['clean_comment'] = cc
        x['org_comment'] = comments[i]
        x['score'] = scores
        dic.append(x)

    return render_template('result.html',n=len(clean_commentso),nn=nn,np=np,nne=nne,dic=dic)


    

    # return clean_commentso12



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
