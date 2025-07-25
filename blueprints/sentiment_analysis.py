from flask import Blueprint, request, render_template, session
from transformers import BartTokenizer, BartForConditionalGeneration

sentiment_analysis_blueprint = Blueprint('sentiment_analysis', __name__)

@sentiment_analysis_blueprint.route('/summarize', methods=['POST'])
def summarize():
    comments = request.form.getlist('clean_commentso')  # Use getlist to get the list of comments
    if not comments:
        return "No comments provided", 400  # Return an error if no comments are provided

    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    text = " ".join(comments)
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summaryy = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    summary = session.get('summary')

    return render_template('summarize.html', summary=summaryy)
