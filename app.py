# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/cloth_item'
METADATA_FILE = 'data/metadata.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Load metadata
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save metadata
def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

@app.route('/')
def index():
    metadata = load_metadata()
    images = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.jpg'):
            tags = metadata.get(filename, [])
            images.append({'filename': filename, 'tags': tags})
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # Remove background and convert to JPG
    input_image = Image.open(file.stream)
    output = remove(input_image)
    img_io = io.BytesIO()
    output.convert('RGB').save(img_io, 'JPEG')
    img_io.seek(0)
    
    # Save to folder
    filename = file.filename.rsplit('.', 1)[0] + '.jpg'  # Ensure .jpg extension
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(img_io.read())
    
    # Initialize metadata
    metadata = load_metadata()
    metadata[filename] = []  # Start with empty tags
    save_metadata(metadata)
    
    return redirect(url_for('index'))

@app.route('/add_tag', methods=['POST'])
def add_tag():
    filename = request.form['filename']
    tag = request.form['tag']
    metadata = load_metadata()
    if filename in metadata:
        if tag not in metadata[filename]:
            metadata[filename].append(tag)
        save_metadata(metadata)
    return redirect(url_for('index'))

@app.route('/remove_tag', methods=['POST'])
def remove_tag():
    filename = request.form['filename']
    tag = request.form['tag']
    metadata = load_metadata()
    if filename in metadata and tag in metadata[filename]:
        metadata[filename].remove(tag)
        save_metadata(metadata)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)