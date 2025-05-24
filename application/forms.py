from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField
from wtforms.validators import DataRequired,ValidationError,Email,Length,EqualTo
from application.models import User

class LogInForm(FlaskForm):
    Email = StringField("Email",validators=[DataRequired(),Email()])
    Password = StringField("Password",validators=[DataRequired(),Length(min=6,max=15)])
    RememberMe  = BooleanField("Remember Me")
    Submit = SubmitField("Login")
     
class SignUpForm(FlaskForm):
    UserName=StringField("Username",validators=[DataRequired(),Length(min=4,max=25)])
    FirstName = StringField("First Name", validators=[DataRequired(),Length(min=2,max=25)])
    LastName = StringField("Last Name", validators=[DataRequired(),Length(min=2,max=25)])
    Email = StringField("Email", validators=[DataRequired(),Email()])
    Password = StringField("Password", validators=[DataRequired()])
    PasswordConfirm = StringField("Confirm Password", validators=[DataRequired(),EqualTo('Password')])
    Submit = SubmitField("Create")

    def validate_Email(self,Email):
        user= User.query.filter_by(Email=Email.data).first()
        if user:
            raise ValidationError("Email is already in use. Pick another one")