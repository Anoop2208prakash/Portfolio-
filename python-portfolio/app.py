import os
import datetime
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
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_123")

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

# --- HELPER FOR CLEANUP ---

def delete_old_asset(setting_name, resource_type="image"):
    existing = db.settings.find_one({"name": setting_name})
    if existing and 'url' in existing:
        image_url = existing['url']
        public_id = image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)

# --- PUBLIC ROUTES ---

@app.route('/')
def home():
    all_projects = list(projects_collection.find())
    all_skills = list(db.skills.find()) # Fetch dynamic skills
    
    cv_data = db.settings.find_one({"name": "cv_link"})
    profile_data = db.settings.find_one({"name": "profile_image"})
    illus_data = db.settings.find_one({"name": "illustration"})

    return render_template('index.html', 
        projects=all_projects, 
        skills=all_skills,
        cv_url=cv_data['url'] if cv_data else "#",
        profile_url=profile_data['url'] if profile_data else "https://via.placeholder.com/400",
        illus_url=illus_data['url'] if illus_data else "https://via.placeholder.com/500"
    )

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if name and email and message:
        db.messages.insert_one({
            "name": name,
            "email": email,
            "message": message,
            "date": datetime.datetime.now()
        })
    return redirect(url_for('home'))

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
    all_messages = list(db.messages.find().sort("date", -1)) 
    all_skills = list(db.skills.find()) # Fetch skills for management
    return render_template('admin.html', 
        projects=all_projects, 
        messages=all_messages, 
        skills=all_skills
    )

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

# --- SKILLS MANAGEMENT ---

@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    skill_name = request.form.get('skill_name')
    icon_class = request.form.get('icon_class') # e.g. 'fa-brands fa-python'
    
    if skill_name and icon_class:
        db.skills.insert_one({
            "name": skill_name,
            "icon": icon_class
        })
    return redirect(url_for('admin'))

@app.route('/delete_skill/<id>')
@login_required
def delete_skill(id):
    db.skills.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('admin'))

# --- ASSET & MESSAGE MANAGEMENT ---

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if 'profile_image' in request.files:
        p_file = request.files['profile_image']
        if p_file.filename != '':
            delete_old_asset("profile_image")
            p_result = cloudinary.uploader.upload(p_file)
            db.settings.update_one({"name": "profile_image"}, {"$set": {"url": p_result['secure_url']}}, upsert=True)
            
    if 'illustration' in request.files:
        i_file = request.files['illustration']
        if i_file.filename != '':
            delete_old_asset("illustration")
            i_result = cloudinary.uploader.upload(i_file)
            db.settings.update_one({"name": "illustration"}, {"$set": {"url": i_result['secure_url']}}, upsert=True)

    if 'cv' in request.files:
        c_file = request.files['cv']
        if c_file.filename != '':
            delete_old_asset("cv_link", resource_type="raw")
            c_result = cloudinary.uploader.upload(c_file, resource_type="raw")
            db.settings.update_one({"name": "cv_link"}, {"$set": {"url": c_result['secure_url']}}, upsert=True)
    return redirect(url_for('admin'))

@app.route('/delete/<id>')
@login_required
def delete(id):
    project = projects_collection.find_one({"_id": ObjectId(id)})
    if project and 'image_url' in project:
        public_id = project['image_url'].split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
    projects_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('admin'))

@app.route('/delete_message/<id>')
@login_required
def delete_message(id):
    db.messages.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)