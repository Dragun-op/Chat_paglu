from application import app  
from flask import render_template,redirect,flash,request,url_for,session
from flask_socketio import send, join_room, emit
from application import db,socketio
from application.models import User, Friendship, Message
from application.forms import LogInForm , SignUpForm

def get_private_room(user1, user2):
    return "_".join(sorted([str(user1), str(user2)]))

@app.route('/')
@app.route('/pagluZone')
def pagluZone():
    return render_template('index.html',title=pagluZone,pagluZone=True)
    # return "<h1>hello shawty</h1>"


@app.route('/yourPaglus',methods=['GET','POST'])
def yourPaglu():
        if 'UserName' not in session:
            return redirect(url_for('login'))

        current_user = User.query.filter_by(UserName=session['UserName']).first()
        search_result = None

        if request.method == 'POST':
            search_username = request.form.get('UserName')
            search_result = User.query.filter_by(UserName=search_username).first()

            if search_result and search_result.UserId != current_user.UserId:

                existing = Friendship.query.filter(
                    ((Friendship.SenderId == current_user.UserId) & (Friendship.ReceiverId == search_result.UserId)) |
                    ((Friendship.ReceiverId == current_user.UserId) & (Friendship.SenderId == search_result.UserId))
                ).first()

                if not existing:
                    new_request = Friendship(SenderId=current_user.UserId, ReceiverId=search_result.UserId)
                    db.session.add(new_request)
                    db.session.commit()
                    flash("Friend request sent!")
                else:
                    flash("Friend request already exists or user is already your friend.")
            else:
                flash("User not found or invalid.")


        friends = Friendship.query.filter(
            ((Friendship.SenderId == current_user.UserId) | (Friendship.ReceiverId == current_user.UserId)) &
            (Friendship.Status == 'accepted')
        ).all()

        return render_template('yourPaglu.html', title="yourPaglu", friends=friends, current_user=current_user)



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
            session['UserId'] = user.UserId
            flash(f"{session['UserName']} logged in succesfully!")
            return redirect(url_for("pagluZone"))
        else:
            flash("Ivalid Credentials")
    return render_template('login.html',title="login",form=form,login=True)



@app.route('/chat/<username>')
def private_chat(username):
    if 'UserName' not in session:
        flash("Login to start chatting.")
        return redirect(url_for('login'))

    current_user = User.query.filter_by(UserName=session['UserName']).first()
    chat_with = User.query.filter_by(UserName=username).first_or_404()

    is_friend = Friendship.query.filter(
        ((Friendship.SenderId == current_user.UserId) & (Friendship.ReceiverId == chat_with.UserId)) |
        ((Friendship.ReceiverId == current_user.UserId) & (Friendship.SenderId == chat_with.UserId)),
        Friendship.Status == 'accepted'
    ).first()

    if not is_friend:
        flash("You can only chat with friends.")
        return redirect(url_for('yourPaglu'))

    return render_template('chat.html',title=f"Chat with {chat_with.UserName}",receiver=chat_with)


@app.route('/notifications')
def notifications():
    if 'UserName' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(UserName=session['UserName']).first()

    requests = Friendship.query.filter_by(ReceiverId=user.UserId, Status='pending').all()

    return render_template('notifications.html', title="Notifications", requests=requests)

@app.route('/accept_request/<int:fid>')
def accept_request(fid):
    request = Friendship.query.get_or_404(fid)
    if request.ReceiverId == User.query.filter_by(UserName=session['UserName']).first().UserId:
        request.Status = 'accepted'
        db.session.commit()
        flash("Friend request accepted!")
    return redirect(url_for('notifications'))


@app.route('/profile')
def profile():
    return render_template('profile.html')



@app.route('/settings')
def settings():
    return render_template('settings.html')



@app.route('/logout')
def logout():
        session.pop('UserId', None)
        session.pop('UserName', None)
        flash("Logged out successfully.")
        return redirect(url_for('login'))


@socketio.on('join_private')
def handle_join(data):
    room = get_private_room(data['sender'], data['receiver'])
    join_room(room)

@socketio.on('private_message')
def handle_private_message(data):
    room = get_private_room(data['sender'], data['receiver'])

    msg = Message(
        SenderId=data['sender_id'],
        ReceiverId=data['receiver_id'],
        Content=data['message']
    )
    db.session.add(msg)
    db.session.commit()

    emit('new_private_message', {
        'sender': data['sender'],
        'message': data['message']
    }, room=room)