import flask
from application import db
from werkzeug.security import generate_password_hash , check_password_hash 

class User(db.Model):
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
    
