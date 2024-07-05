from flask import Blueprint, request, jsonify, render_template, session
from utils.youtube_api import get_comments
from utils.text_cleaning import clean_comments, map_comments_to_labels
from transformers import pipeline
from transformers import BartTokenizer, BartForConditionalGeneration


youtube_comments_blueprint = Blueprint('youtube_comments', __name__)

@youtube_comments_blueprint.route('/')
def index():
    return render_template('index.html')

@youtube_comments_blueprint.route('/results', methods=['GET'])
def results():
    url = request.args.get('url')
    video_id = extract_video_id(url)
    if video_id:
        comments = get_comments(video_id)
    else:
        return jsonify({'error': 'Invalid URL'}), 400

    n = len(comments)
    comments = comments[:200] if n >= 200 else comments[:]

    clean_commentso = clean_comments(comments)
    sentiment_model = pipeline(model="Purushotham2003/finetuning-sentiment-model-3000-samples")
    clean_commentso1 = sentiment_model(clean_commentso)
    clean_commentso12 = map_comments_to_labels(clean_commentso, clean_commentso1)

    print(clean_commentso12)
    predictions, scores, np, nn, nne = [], [], 0, 0, 0

    for sentiment_dict in clean_commentso1:
        label = sentiment_dict["label"]
        score = sentiment_dict["score"]
        scores.append(score)
        if label == 'LABEL_1':
            predictions.append('POSITIVE')
            np += 1
        elif label == 'LABEL_0':
            predictions.append('NEGATIVE')
            nn += 1
        else:
            predictions.append('NEUTRAL')
            nne += 1

    dic = [{'sent': predictions[i], 'clean_comment': cc, 'org_comment': cc, 'score': scores} for i, cc in enumerate(clean_commentso)]

    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    text = " ".join(clean_commentso)
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    session['summary'] = summary

    print(summary)
    return render_template('result.html', n=len(clean_commentso), nn=nn, np=np, nne=nne, dic=dic)

def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path.lstrip('/')
    else:
        query = parsed_url.query
        params = parse_qs(query)
        return params.get('v', [None])[0]
