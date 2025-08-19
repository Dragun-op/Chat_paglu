# 💬 ChatPaglu

A real-time chat web application built with **Flask**, **Flask-SocketIO**, and **Flask-Mail**. It supports private 1-to-1 chatting, friend requests, OTP-based authentication, profile management, and notifications.

---

## 🚀 Features

- 🔐 **User Authentication**
  - Signup with email verification via OTP
  - Secure login/logout with password hashing
  - Remember Me functionality

- 👥 **Friends System**
  - Send and accept friend requests
  - Remove friends
  - Notifications for pending requests

- 💬 **Real-time Private Chat**
  - One-to-one chat with WebSocket (Socket.IO)
  - Messages stored in the database
  - Seen/unseen status tracking

- 📝 **Profile & Settings**
  - Update profile info (username, name, email, password)
  - Email change verification via OTP
  - Account deletion with password confirmation

- ⚡ **Other**
  - Session handling with Flask
  - Flash messages for feedback
  - Bootstrap/Jinja2-powered templates

---

## 🛠️ Tech Stack

- **Backend:** Flask, Flask-SocketIO, Flask-Mail, SQLAlchemy
- **Frontend:** Jinja2, HTML, CSS, Bootstrap
- **Database:** SQLite / PostgreSQL (SQLAlchemy ORM)
- **Other:** WebSockets for live chat

---

## 📂 Project Structure

```
CHAT-APP/
│
├── application/
│   ├── __init__.py          # App, DB, SocketIO, Mail initialization
│   ├── forms.py             # WTForms for signup, login, profile updates
│   ├── models.py            # Database models (User, Messages, Friendships)
│   ├── routes.py            # Flask routes & socket event handlers
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates (Jinja2)
│
├── config.py                # App configuration
├── main.py                  # Entry point to run the app
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables
├── .flaskenv              # Flask environment config
└── .gitignore             # Git ignored files
```

---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/chatpaglu.git
cd chatpaglu
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

**Ensure `.flaskenv` contains:**

```env
FLASK_APP=main.py
FLASK_ENV=development
```

### 5. Initialize the database

```bash
flask shell
```

```python
>>> from application import db
>>> db.create_all()
>>> exit()
```

### 6. Run the app

**Standard run:**
```bash
flask run
```

**Or directly with Python (SocketIO enabled):**
```bash
python main.py
```

### ✅ Now your app should be live at:

👉 **http://127.0.0.1:5000**

---

## 🔮 Future Improvements (Maybe)

- Group chat support
- Message reactions & typing indicators
- Dark mode UI
- Deployment on Heroku/Render with PostgreSQL

---

*Made with ❤️ using Flask and Socket.IO*
