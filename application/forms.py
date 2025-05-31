from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField
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
        
class UpdateProfileForm(FlaskForm):
    UserName = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    FirstName = StringField("First Name", validators=[DataRequired()])
    LastName = StringField("Last Name", validators=[DataRequired()])
    Email = StringField("Email", validators=[DataRequired(), Email()])
    CurrentPassword = PasswordField("Current Password", validators=[DataRequired()])
    NewPassword = PasswordField("New Password", validators=[])
    ConfirmPassword = PasswordField("Confirm Password", validators=[EqualTo('NewPassword', "Passwords must match")])
    Submit = SubmitField("Save Changes")

    def validate_UserName(self, field):
        user = User.query.filter_by(UserName=field.data).first()
        if user and user.UserName != self.original_username:
            raise ValidationError('Username already taken.')

    def validate_Email(self, field):
        user = User.query.filter_by(Email=field.data).first()
        if user and user.Email != self.original_email:
            raise ValidationError('Email already in use.')