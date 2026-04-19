from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectMultipleField, SelectField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
import sqlalchemy as sqla
from app import db
from app.main.models import Student, Faculty
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import Major, Student, Topic, Coursework, Languages
from faculty_data import faculty

choices_list = [(f["email"], f"{f['firstname']} {f['lastname']} ({f['email']})") for f in faculty]

class FacultyRegistrationForm(FlaskForm):
    email =  SelectField('Find your name or email:', choices=choices_list)
    username = StringField('Choose Username', validators=[DataRequired()])
    password = PasswordField('Choose Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Activate')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    firstname = StringField('First Name', validators = [DataRequired()])
    lastname = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField('Password', validators = [DataRequired(), EqualTo('password')])
    gpa = StringField('GPA', validators=[DataRequired()])

    majors_of_student = QuerySelectMultipleField ('Majors',
                query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),   
                get_label= lambda theMajor : theMajor.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    topics_students = QuerySelectMultipleField ('Topic',
                query_factory=lambda: db.session.scalars(sqla.select(Topic).order_by(Topic.name)),   
                get_label= lambda theTopic : theTopic.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    languages_students = QuerySelectMultipleField ('Languages',
                query_factory=lambda: db.session.scalars(sqla.select(Languages).order_by(Languages.name)),   
                get_label= lambda theLanguage : theLanguage.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    coursework_students = QuerySelectMultipleField ('Coursework',
                query_factory=lambda: db.session.scalars(sqla.select(Coursework).order_by(Coursework.title)),   
                get_label= lambda theCoursework : theCoursework.title,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    submit = SubmitField('Register')

    def validate_username(self, username):
        query = sqla.select(Student).where(Student.username == username.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('The username already exists! Please use a different username.')
        
    def validate_email(self, email):
        query = sqla.select(Student).where(Student.email == email.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('The email already exists! Please use a different email.')

class LoginForm(FlaskForm):
    
    password = PasswordField('Password', validators = [DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

