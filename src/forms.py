from flask_wtf import FlaskForm
from wtforms import (StringField, DateField, IntegerField, 
                     TextAreaField, TimeField, PasswordField)
from wtforms.validators import (DataRequired, regexp, Email, 
                                Length, EqualTo, ValidationError)
import models


class NewEntryForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired()]
    )
    
    date = DateField(
        "Date", 
        format="%d/%m/%Y",
        validators=[]
    )

    time_spent = IntegerField(
        "Time Spent",
        validators=[DataRequired()]
    )

    learned = TextAreaField(
        "What I Learned",
        validators=[DataRequired()]
    )

    resourses = TextAreaField(
        "Resources to Remember",
        validators=[DataRequired()]
    )

    tag = StringField(
        "Tag",
        validators=[DataRequired()]
    )


def user_exist(form, field):
    if models.User.select().where(models.User.username == field.data).exists():
        raise ValidationError("This user already exist!")


def email_exist(form, field):
    if models.User.select().where(models.User.email == field.data).exists():
        raise ValidationError("This email already exist!")


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            regexp(
                r'^[a-zA-Z0-9_.]+$',
                message="Username must contain character, "
                "number and underscore only"
            ),
            user_exist]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exist]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="The Password must match"),
            Length(min=2)]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired()
        ])
    password = PasswordField(
        'Password',
        validators=[DataRequired()])
