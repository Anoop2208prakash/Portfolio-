import os
from flask import Flask, render_template, request, redirect, url_for, session
from database import db, projects_collection 
import cloudinary
import cloudinary.uploader
from bson.objectid import ObjectId
from dotenv import load_dotenv
from functools import wraps

# 1. Setup
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_123") # For session security

# 2. Cloudinary Config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# 3. Security Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- PUBLIC ROUTES ---

@app.route('/')
def home():
    all_projects = list(projects_collection.find())
    # Fetch the latest CV link from the settings collection
    cv_data = db.settings.find_one({"name": "cv_link"})
    cv_url = cv_data['url'] if cv_data else "#"
    return render_template('index.html', projects=all_projects, cv_url=cv_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# --- ADMIN ROUTES (PROTECTED) ---

@app.route('/admin')
@login_required
def admin():
    all_projects = list(projects_collection.find())
    return render_template('admin.html', projects=all_projects)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_file = request.files['image']
        
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            projects_collection.insert_one({
                "title": title,
                "description": description,
                "image_url": upload_result['secure_url']
            })
            return redirect(url_for('admin'))
            
    return render_template('add_project.html')

@app.route('/upload_cv', methods=['POST'])
@login_required
def upload_cv():
    cv_file = request.files['cv']
    if cv_file:
        # Use resource_type="raw" for PDF files in Cloudinary
        upload_result = cloudinary.uploader.upload(cv_file, resource_type="raw")
        db.settings.update_one(
            {"name": "cv_link"}, 
            {"$set": {"url": upload_result['secure_url']}}, 
            upsert=True
        )
    return redirect(url_for('admin'))

@app.route('/delete/<id>')
@login_required
def delete(id):
    projects_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)