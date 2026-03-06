print("### RUNNING UPDATED app.py WITH KEYWORD OVERRIDE ###")

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
import os
from langdetect import detect
from googletrans import Translator
from transformers import pipeline

# =======================
# APP CONFIG
# =======================
app = Flask(__name__)
app.secret_key = "sentiment_dashboard_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =======================
# LOGIN MANAGER
# =======================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =======================
# HUGGING FACE EMOTION API
# =======================
API_URL = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-xlm-roberta-base-emotion"

HEADERS = {
    "Authorization": "your token"
}
EMOTION_KEYWORDS = {
    "Anger": ["angry", "rage", "pissed", "poda", "loosu", "idiot", "hate", "worst", "cheap", "bad", "terrible", "awful", "horrible", "stupid", "annoyed", "frustrated", "gussa", "angry", "furious", "mad", "irritated", "annoyed"],
    "Sadness": ["sad", "depressed", "lonely", "cry", "miss", "pain", "unhappy", "sorrow", "grief", "heartbroken", "disappointed"],
    "Fear": ["scared", "afraid", "fear", "dar", "bayam", "terrified", "anxious", "worried", "panic"],
    "Joy": ["happy", "love", "super", "awesome", "best", "nice", "good", "great", "excellent", "wonderful", "excited", "joyful", "pleased"],
    "Disgust": ["disgust", "dirty", "gross", "mosham", "nasty", "repulsive", "disgusting", "yuck"],
    "Surprise": ["surprise", "surprised", "amazing", "shocked", "wow", "unexpected", "astonished", "stunned"],
    "Love": ["love", "loving", "adore", "beloved", "dear", "affection", "caring", "romantic", "passionate"],
    "Neutral": ["okay", "fine", "normal", "average", "regular", "standard", "ordinary", "common", "usual"]
}

# Local emotion model as fallback
emotion_pipeline = None
def get_emotion_pipeline():
    global emotion_pipeline
    if emotion_pipeline is None:
        emotion_pipeline = pipeline("text-classification", model="cardiffnlp/twitter-xlm-roberta-base-emotion", return_all_scores=True)
    return emotion_pipeline

def predict_emotion(text):
    # Detect language
    try:
        if not text.strip():  # Empty or whitespace only
            lang = 'en'
        else:
            lang = detect(text)
    except:
        lang = 'en'  # Default to English if detection fails

    # Translate to English if not already English
    if lang != 'en':
        try:
            translator = Translator()
            translated_text = translator.translate(text, src=lang, dest='en').text
            print(f"DEBUG: Translated '{text}' from {lang} to '{translated_text}'")
            text = translated_text
        except Exception as e:
            print(f"DEBUG: Translation failed for '{text}': {e}, using original text")
            # Use original text if translation fails

    text_lower = text.lower()

    # 🔴 HARD RULE OVERRIDE (WILL ALWAYS TRIGGER)
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for word in keywords:
            if word in text_lower:
                print(f"DEBUG: Keyword '{word}' matched → {emotion}")
                return emotion, 95.0

    # 🟡 FALLBACK TO API
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": text}
    )

    if response.status_code != 200:
        print(f"DEBUG: API error status {response.status_code}: {response.text}")
        return "Neutral", 50.0  # Fallback emotion

    json_response = response.json()
    if isinstance(json_response, dict) and 'error' in json_response:
        print(f"DEBUG: API error: {json_response['error']}")
        return "Neutral", 50.0  # Fallback emotion

    if not isinstance(json_response, list) or len(json_response) == 0:
        print(f"DEBUG: Unexpected API response format: {json_response}")
        return "Neutral", 50.0  # Fallback emotion

    results = json_response[0]
    if not isinstance(results, list) or len(results) == 0:
        print(f"DEBUG: No results in API response: {results}")
        return "Neutral", 50.0  # Fallback emotion

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    emotion = results[0]["label"].capitalize()
    confidence = round(results[0]["score"] * 100, 2)

    print("DEBUG: API fallback →", emotion, confidence)
    return emotion, confidence




# =======================
# DATABASE MODELS
# =======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=True)
    media_path = db.Column(db.String(255), nullable=True)
    media_type = db.Column(db.String(50), nullable=True)  # 'video' or 'image'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(30), nullable=False)  # Emotion name
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

# =======================
# AUTH ROUTES
# =======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =======================
# FEED ROUTES
# =======================
@app.route("/")
@login_required
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template("feed.html", posts=posts)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        text = request.form.get("text")
        media_file = request.files.get("video")
        media_path = None
        media_type = None

        if media_file and media_file.filename:
            media_path = f"uploads/{media_file.filename}"
            media_file.save(os.path.join(app.root_path, "static", media_path))
            # Determine media type based on mimetype
            if media_file.mimetype.startswith('video/'):
                media_type = 'video'
            elif media_file.mimetype.startswith('image/'):
                media_type = 'image'

        post = Post(text=text, media_path=media_path, media_type=media_type, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("upload.html")

# =======================
# COMMENT ROUTE (EMOTION)
# =======================
@app.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment(post_id):
    text = request.form["comment"]

    emotion, confidence = predict_emotion(text)

    comment_obj = Comment(
        text=text,
        sentiment=emotion,
        confidence=confidence,
        post_id=post_id,
        user_id=current_user.id
    )

    db.session.add(comment_obj)
    db.session.commit()
    return redirect(url_for("index"))

# =======================
# DELETE POST
# =======================
@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return "Unauthorized", 403

    Comment.query.filter_by(post_id=post_id).delete()

    if post.media_path:
        path = os.path.join(app.root_path, "static", post.media_path)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

# =======================
# POST EMOTION REPORT (Per Post Analysis)
# =======================
@app.route("/report/<int:post_id>")
@login_required
def post_report(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    
    # Aggregate emotions
    emotion_counts = {}
    emotion_data = []
    
    for comment in comments:
        emotion = comment.sentiment
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        emotion_data.append({
            'text': comment.text,
            'sentiment': emotion,
            'confidence': comment.confidence,
            'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Calculate percentages
    total_comments = len(comments)
    emotion_percentages = {}
    for emotion, count in emotion_counts.items():
        emotion_percentages[emotion] = round((count / total_comments) * 100, 2) if total_comments > 0 else 0
    
    return render_template("report.html", 
                           post=post, 
                           comments=comments,
                           emotion_counts=emotion_counts,
                           emotion_percentages=emotion_percentages,
                           total_comments=total_comments)

# =======================
# RUN APP
# =======================
if __name__ == "__main__":
    app.run(debug=True)
