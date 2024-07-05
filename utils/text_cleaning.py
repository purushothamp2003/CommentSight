import re
import emoji
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()
stop_words = stopwords.words('english')

def clean_comment(comment):
    comment = comment.lower()
    comment = re.sub(r'[^\w\s]', '', comment)
    comment = emoji.demojize(comment, delimiters="_")
    comment = re.sub(r'\s\s+', ' ', comment)
    return comment

def clean_comments(comments):
    cleaned_comments = []
    for comment in comments:
        cleaned_comment = clean_comment(comment)
        try:
            if detect(cleaned_comment) == 'en':
                cleaned_comments.append(cleaned_comment)
        except:
            pass
    return cleaned_comments

def map_comments_to_labels(clean_comments, sentiment_analysis_output):
    if len(clean_comments) != len(sentiment_analysis_output):
        raise ValueError("Lengths of comments and sentiment analysis output don't match!")

    comment_label_pairs = []
    for i in range(len(clean_comments)):
        comment = clean_comments[i]
        sentiment_dict = sentiment_analysis_output[i]
        label = sentiment_dict["label"]
        comment_label_pairs.append((comment, label))

    return comment_label_pairs
