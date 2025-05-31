from application import app  
from flask import render_template,redirect,flash,request,url_for,session
from flask_socketio import send, join_room, emit
from application import db,socketio,mail
from flask_mail import Message
from application.models import User, Friendship, Messages
from application.forms import LogInForm , SignUpForm , UpdateProfileForm
import random
from datetime import timedelta

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

@app.route('/remove_friend/<int:friend_id>', methods=['POST'])
def remove_friend(friend_id):
    if 'UserName' not in session:
        return redirect(url_for('login'))

    friendship = Friendship.query.get_or_404(friend_id)
    current_user_id = session['UserId']

    if friendship.SenderId == current_user_id or friendship.ReceiverId == current_user_id:
        db.session.delete(friendship)
        db.session.commit()
        flash("Friend removed successfully.")
    else:
        flash("You are not authorized to perform this action.")

    return redirect(url_for('yourPaglu'))

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
        
        otp = random.randint(100000, 999999)
        session['otp'] = str(otp)
        session['pending_user'] = {
            'UserName': form.UserName.data,
            'FirstName': form.FirstName.data,
            'LastName': form.LastName.data,
            'Email': form.Email.data,
            'Password': form.Password.data
        }

        msg = Message(
            "Chatpaglu Email Verification OTP",
            recipients=[form.Email.data],
            sender=app.config["MAIL_DEFAULT_SENDER"]
        )

        msg.body = f"Your OTP for Chatpaglu registration is: {otp}"
        try:
            mail.send(msg)
        except Exception as e:
            print(e)
            flash("Failed to send OTP. Please try again.")
            return redirect(url_for("signup"))

        flash("OTP sent to your email. Please verify to complete signup.")
        return redirect(url_for('verify_otp'))
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
                
    return render_template('signup.html',title="signup",form=form,signup=True)


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if str(session.get('otp')) == user_otp:
            data = session.get('pending_user')
            if data:
                new_user = User(
                    UserName=data['UserName'],
                    FirstName=data['FirstName'],
                    LastName=data['LastName'],
                    Email=data['Email']
                )
                new_user.SetPassword(data['Password'])
                db.session.add(new_user)
                db.session.commit()

                session.pop('otp')
                session.pop('pending_user')
                flash("Email verified. Account created successfully!")
                return redirect(url_for('login'))
        else:
            flash("Invalid OTP. Please try again.")

    return render_template('verify_otp.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('UserName'):
        return redirect(url_for('pagluZone'))
    
    form = LogInForm()
    if form.validate_on_submit():
        Email = form.Email.data
        Password = form.Password.data

        user = User.query.filter_by(Email=Email).first()
        if user and user.CheckPassword(Password):
            session['UserId'] = user.UserId
            session['UserName'] = user.UserName

            if form.RememberMe.data:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False

            flash(f"{session['UserName']} logged in successfully!")
            return redirect(url_for("pagluZone"))
        else:
            flash("Invalid Credentials")

    return render_template('login.html', title="login", form=form, login=True)




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
    
    messages = Messages.query.filter(
        ((Messages.SenderId == current_user.UserId) & (Messages.ReceiverId == chat_with.UserId)) |
        ((Messages.SenderId == chat_with.UserId) & (Messages.ReceiverId == current_user.UserId))
                                    ).order_by(Messages.Timestamp).all()

    return render_template('chat.html',title=f"Chat with {chat_with.UserName}",receiver=chat_with,sender=current_user,messages=messages)


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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'UserName' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(UserName=session['UserName']).first()
    form = UpdateProfileForm(obj=user)
    form.original_username = user.UserName
    form.original_email = user.Email

    if form.validate_on_submit():
        if not user.CheckPassword(form.CurrentPassword.data):
            flash("Incorrect current password.", "danger")
        else:

            if form.Email.data != user.Email:
                otp = random.randint(100000, 999999)
                session['email_otp'] = str(otp)
                session['new_email'] = form.Email.data
                session['pending_updates'] = {
                    'UserName': form.UserName.data,
                    'FirstName': form.FirstName.data,
                    'LastName': form.LastName.data,
                    'NewPassword': form.NewPassword.data
                }

                msg = Message("Verify Your New Email", recipients=[form.Email.data])
                msg.body = f"Your verification OTP is: {otp}"
                try:
                    mail.send(msg)
                    flash("OTP sent to new email. Please verify.", "info")
                    return redirect(url_for('verify_email_update'))
                except Exception as e:
                    flash("Failed to send OTP. Please try again.", "danger")
                    return redirect(url_for('profile'))
                
            user.UserName = form.UserName.data
            user.FirstName = form.FirstName.data
            user.LastName = form.LastName.data
            if form.NewPassword.data:
                user.SetPassword(form.NewPassword.data)
            db.session.commit()
            session['UserName'] = user.UserName
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")

    return render_template('profile.html', title="View Profile", form=form)


@app.route('/verify-email-update', methods=['GET', 'POST'])
def verify_email_update():
    if 'email_otp' not in session or 'new_email' not in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if entered_otp == session['email_otp']:
            user = User.query.get(session['UserId'])

            updates = session.get('pending_updates', {})
            user.Email = session['new_email']
            user.UserName = updates.get('UserName', user.UserName)
            user.FirstName = updates.get('FirstName', user.FirstName)
            user.LastName = updates.get('LastName', user.LastName)

            if updates.get('NewPassword'):
                user.SetPassword(updates['NewPassword'])

            db.session.commit()
            session['UserName'] = user.UserName
            flash("Email updated and verified successfully!", "success")

            session.pop('email_otp')
            session.pop('new_email')
            session.pop('pending_updates')

            return redirect(url_for('profile'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('verify_email_update.html')


@app.route('/settings', methods=['GET','POST'])
def settings():
    if 'UserName' not in session:
        return redirect(url_for('login'))

    return render_template('settings.html', title="Settings")

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'UserName' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(UserName=session['UserName']).first()
    entered_password = request.form.get('delete_password')

    if not user or not user.CheckPassword(entered_password):
        flash("Incorrect password. Account not deleted.", "danger")
        return redirect(url_for('profile'))

    Friendship.query.filter((Friendship.SenderId == user.UserId) | (Friendship.ReceiverId == user.UserId)).delete()

    Messages.query.filter((Messages.SenderId == user.UserId) | (Messages.ReceiverId == user.UserId)).delete()

    db.session.delete(user)
    db.session.commit()

    session.clear()
    flash("Your account has been permanently deleted.", "info")
    return redirect(url_for('signup'))

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

    msg = Messages(
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