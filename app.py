from flask import Flask
from blueprints.youtube_comments import youtube_comments_blueprint
from blueprints.sentiment_analysis import sentiment_analysis_blueprint
from blueprints.text_processing import text_processing_blueprint
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Set your secret key here

# Register blueprints
app.register_blueprint(youtube_comments_blueprint)
app.register_blueprint(sentiment_analysis_blueprint)
app.register_blueprint(text_processing_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
