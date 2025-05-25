from application import app  
from flask import render_template,redirect,flash,request,url_for,session
from flask_socketio import send
from application import db,socketio
from application.models import User
from application.forms import LogInForm , SignUpForm

@app.route('/')
@app.route('/index')
@app.route('/pagluZone')
def pagluZone():
    return render_template('index.html',title=pagluZone,pagluZone=True)
    # return "<h1>hello shawty</h1>"

@app.route('/yourPaglus')
def yourPaglu():
    return render_template('yourPaglu.html',title=yourPaglu)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if session.get('UserName'):
        return redirect(url_for('pagluZone'))
    form = SignUpForm()
    if form.validate_on_submit()==True:
        existing_user = User.query.filter_by(UserName=form.UserName.data).first()
        if existing_user:
            flash("Username already exists. Please choose another.")
            return redirect(url_for("login"))
        
        else:
            new_user= User(
                    UserName=form.UserName.data,
                    FirstName=form.FirstName.data,
                    LastName=form.LastName.data,
                    Email=form.Email.data,)
            
            new_user.SetPassword(form.Password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Your Account has been created successfully!!")
            return redirect(url_for("login"))
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
                
    return render_template('signup.html',title="signup",form=form,signup=True)

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('UserName'):
        return redirect(url_for('pagluZone'))
    form = LogInForm()
    if form.validate_on_submit()==True:
        Email = form.Email.data
        Password = form.Password.data

        user= User.query.filter_by(Email=Email).first()
        if user and user.CheckPassword(Password):
            session['UserName'] = user.UserName
            flash(f"{session['UserName']} logged in succesfully!")
            return redirect(url_for("pagluZone"))
        else:
            flash("Ivalid Credentials")
    return render_template('login.html',title="login",form=form,login=True)

@app.route('/chat')
def chat():
    if 'UserName' not in session:
        flash("Please log in to access the chat.")
        return redirect(url_for("login"))
    return render_template('chat.html', username=session['UserName'])

@socketio.on('message')
def handle_message(msg):
    print('Received message:', msg)
    send(msg, broadcast=True)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
        session.pop('UserName', None)
        flash("Logged out successfully.")
        return redirect(url_for('login'))