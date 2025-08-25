from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
import logging
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import json
from werkzeug.utils import secure_filename
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 5 MB max upload size
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Verify email configuration
logger.debug(f"Mail server: {app.config['MAIL_SERVER']}")
logger.debug(f"Mail port: {app.config['MAIL_PORT']}")
logger.debug(f"Mail username: {app.config['MAIL_USERNAME']}")
logger.debug(f"Mail password set: {'Yes' if app.config['MAIL_PASSWORD'] else 'No'}")

mail = Mail(app)

# Load the trained model
MODEL_PATH = 'tomato_disease_cnn_model.h5'
try:
    model = load_model(MODEL_PATH)
    # Optional warmup to reduce first-request latency
    try:
        dummy_input = np.zeros((1, 128, 128, 3), dtype=np.float32)
        _ = model.predict(dummy_input)
    except Exception as warmup_err:
        logger.warning(f"Model warmup failed: {warmup_err}")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Define class names (ensure this matches your model's training)
# Attempt to load from class_names.json if available to avoid drift
DEFAULT_CLASS_NAMES = [
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

CLASS_NAMES = DEFAULT_CLASS_NAMES
LABELS_PATH = os.path.join(os.path.dirname(__file__), 'class_names.json')
if os.path.exists(LABELS_PATH):
    try:
        with open(LABELS_PATH, 'r', encoding='utf-8') as f:
            loaded_labels = json.load(f)
        if isinstance(loaded_labels, list) and all(isinstance(x, str) for x in loaded_labels):
            CLASS_NAMES = loaded_labels
            logger.info(f"Loaded {len(CLASS_NAMES)} class labels from class_names.json")
        else:
            logger.warning("class_names.json content invalid; falling back to default labels")
    except Exception as e:
        logger.warning(f"Failed to load class_names.json: {e}; falling back to default labels")

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(img, model_to_use):
    if model_to_use is None:
        return "Model not loaded", 0

    img = img.resize((128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model_to_use.predict(img_array)
    predicted_class_index = np.argmax(predictions[0])
    confidence = np.max(predictions[0])
    predicted_class_name = CLASS_NAMES[predicted_class_index]

    return predicted_class_name, confidence

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed: jpg, jpeg, png, webp', 'error')
            return redirect(request.url)

        if model is None:
            flash('Model not loaded. Please try again later.', 'error')
            return redirect(url_for('predict'))

        try:
            # Secure and unique filename
            original_filename = secure_filename(file.filename)
            unique_name = f"{uuid4().hex}_{original_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

            # Save to disk
            file.save(filepath)

            # Validate and open image from saved path
            with Image.open(filepath) as opened_img:
                opened_img = opened_img.convert('RGB')
                prediction, confidence = predict_image(opened_img, model)

            img_url = url_for('static', filename=f"uploads/{unique_name}")
            return render_template('predict.html', prediction=f'{prediction} (Confidence: {confidence:.2f})', img_path=img_url)
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            flash('An error occurred during prediction.', 'error')
            return redirect(url_for('predict'))

    return render_template("predict.html", prediction=None)

@app.route('/healthz', methods=['GET'])
def healthz():
    status = {
        'status': 'ok',
        'model_loaded': model is not None,
        'num_classes': len(CLASS_NAMES) if isinstance(CLASS_NAMES, list) else 0
    }
    return jsonify(status), 200

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Basic validation
        if not all([name, email, message]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('contact'))
        
        try:
            # Create email message
            msg = Message(
                subject=f'New Contact Form Submission from {name}',
                recipients=[os.getenv('MAIL_USERNAME')],  # Your email address
                body=f'''
                Name: {name}
                Email: {email}
                Message: {message}
                '''
            )
            
            # Send email
            logger.debug("Attempting to send email...")
            mail.send(msg)
            logger.debug("Email sent successfully!")
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
            flash(f'An error occurred while sending your message: {str(e)}', 'error')
            return redirect(url_for('contact'))
    
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)  # gunicorn will handle binding/host

