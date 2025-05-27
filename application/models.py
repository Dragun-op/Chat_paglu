import flask
from application import db
from datetime import datetime 
from werkzeug.security import generate_password_hash , check_password_hash 


class User(db.Model):
    __tablename__ = "User"

    UserId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName=db.Column(db.String(50),unique=True)
    FirstName=db.Column(db.String(50),nullable=False)
    LastName=db.Column(db.String(50),nullable=False)
    Email = db.Column(db.String(120),unique=True, nullable=False)
    Password=db.Column(db.String,nullable=False)

    def SetPassword(self,Password):
        self.Password = generate_password_hash(Password)
    
    def CheckPassword(self,Password):
        return check_password_hash(self.Password,Password)
    

    
class Friendship(db.Model):
    __tablename__ = "Friendship"

    FId=db.Column(db.Integer, primary_key=True, autoincrement=True)
    SenderId=db.Column(db.Integer,db.ForeignKey("User.UserId"),nullable=False)
    ReceiverId=db.Column(db.Integer,db.ForeignKey("User.UserId"),nullable=False)
    Status=db.Column(db.String(50),nullable=False,default="pending")
    TimeStamp=db.Column(db.DateTime,unique=True,default=datetime.utcnow)

    Sender = db.relationship('User', foreign_keys=[SenderId], backref='SentRequests')
    Receiver = db.relationship('User', foreign_keys=[ReceiverId], backref='ReceivedRequests')



class Message(db.Model):
    __tablename__ = 'Message'

    MId = db.Column(db.Integer, primary_key=True)
    SenderId = db.Column(db.Integer, db.ForeignKey('User.UserId'), nullable=False)
    ReceiverId = db.Column(db.Integer, db.ForeignKey('User.UserId'), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    Sender = db.relationship('User', foreign_keys=[SenderId], backref='SentMessages')
    Receiver = db.relationship('User', foreign_keys=[ReceiverId], backref='ReceivedMessages')

    def __repr__(self):
        return f"<Message Id={self.Id} From={self.SenderId} To={self.ReceiverId} @ {self.Timestamp}>"