# **Dynamic Full-Stack Portfolio**

A professional, responsive portfolio website built with a **Python/Flask** backend and **MongoDB** for data persistence. This project features a secure administrative dashboard for real-time project management and automated asset handling via **Cloudinary**.



* **Secure Admin Panel**: A protected dashboard for managing project entries and updating professional credentials.
* **Dynamic Project Gallery**: Automatically renders projects stored in MongoDB, allowing for easy updates without redeploying code.
* **Automated Asset Management**: Integrates with Cloudinary API for high-performance image hosting and PDF resume management.
* **Session-Based Authentication**: Implements custom decorators for secure access to administrative routes.
* **Responsive Design**: A clean, modern UI styled with custom CSS for optimal viewing across mobile and desktop devices.

## **🛠️ Tech Stack**

* **Backend**: Python, Flask
* **Database**: MongoDB (NoSQL)
* **Media Storage**: Cloudinary (CDN)
* **Environment Management**: Python-Dotenv
* **Deployment**: Gunicorn, Render/Railway

## **📂 Project Structure**

```text
python-portfolio/
├── app.py              # Main application logic and routing
├── database.py         # MongoDB connection and collection initialization
├── static/             # Stylesheets and client-side assets
│   └── style.css
├── templates/          # Jinja2 HTML templates
│   ├── index.html      # Public-facing portfolio
│   ├── admin.html      # Project/CV management dashboard
│   └── login.html      # Admin authentication portal
├── Procfile            # Deployment instructions for cloud platforms
├── .env.example        # Template for required environment variables
└── requirements.txt    # Project dependencies

```

## **⚙️ Installation & Setup**

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/python-portfolio.git
cd python-portfolio

```


2. **Set Up Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/macOS

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Configure Environment Variables**
Create a `.env` file in the root directory and add your credentials:
```ini
MONGO_URI=your_mongodb_connection_string
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
SECRET_KEY=your_secret_key

```


5. **Run Locally**
```bash
python app.py

```



## **📝 License**

Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed by Anoop Prakash** – [GitHub](https://github.com/Anoop2208prakash) | [LinkedIn](https://www.linkedin.com/in/anoop-prakash-abb101353/)

---
