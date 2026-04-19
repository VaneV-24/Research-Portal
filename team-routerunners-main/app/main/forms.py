from app import db
import sqlalchemy as sqla
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo, Optional
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.widgets import ListWidget, CheckboxInput
from flask_login import current_user
from app.main.models import Major, Student, Topic, Coursework, Languages
from datetime import datetime

class PositionsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[Length(min=1, max=2000)])
    startdate = StringField('Start Date (YYYY-MM-DD)', validators=[DataRequired()])
    enddate = StringField('End Date (YYYY-MM-DD)', validators=[DataRequired()])
    team_size = StringField('Team Size', validators=[DataRequired(), Length(min=1)]) 
    min_gpa = StringField('Minimum GPA', validators=[DataRequired(), Length(min=1)]) 

    majors_of_position = QuerySelectMultipleField('Majors',
                                 query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)),
                                 get_label=lambda m: m.name,
                                 widget=ListWidget(prefix_label=False),
                                 option_widget=CheckboxInput()) 

    topics_position = QuerySelectMultipleField('Topic',
                                 query_factory=lambda: db.session.scalars(sqla.select(Topic).order_by(Topic.name)),
                                 get_label=lambda t: t.name,
                                 widget=ListWidget(prefix_label=False),
                                 option_widget=CheckboxInput()) 

    languages_position = QuerySelectMultipleField('Languages',
                                 query_factory=lambda: db.session.scalars(sqla.select(Languages).order_by(Languages.name)),
                                 get_label=lambda l: l.name,
                                 widget=ListWidget(prefix_label=False),
                                 option_widget=CheckboxInput()) 

    coursework_position = QuerySelectMultipleField('Coursework',
                                 query_factory=lambda: db.session.scalars(sqla.select(Coursework).order_by(Coursework.title)),
                                 get_label=lambda c: c.title,
                                 widget=ListWidget(prefix_label=False),
                                 option_widget=CheckboxInput())
    reference_required = BooleanField('Reference Required?')        
    submit = SubmitField('Post')          

    # Custom validator to ensure enddate >= startdate
    def validate_enddate(self, field):
        try:
            start = datetime.strptime(self.startdate.data, "%Y-%m-%d")
            end = datetime.strptime(field.data, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Dates must be in YYYY-MM-DD format.")

        if end < start:
            raise ValidationError("End date cannot be before start date.")

class EditStudentForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    firstname = StringField('First Name', validators = [DataRequired()])
    lastname = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField('Password', validators = [DataRequired(), EqualTo('password')])
    gpa = StringField('GPA', validators= [DataRequired()])

    #Select Fields
    majors = QuerySelectMultipleField ('Majors',
                query_factory=lambda: db.session.scalars(sqla.select(Major).order_by(Major.name)).all(),   
                get_label= lambda theMajor : theMajor.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    topics = QuerySelectMultipleField ('Topic',
                query_factory=lambda: db.session.scalars(sqla.select(Topic).order_by(Topic.name)).all(),   
                get_label= lambda theTopic : theTopic.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    languages = QuerySelectMultipleField ('Languages',
                query_factory=lambda: db.session.scalars(sqla.select(Languages).order_by(Languages.name)).all(),   
                get_label= lambda theLanguage : theLanguage.name,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    coursework = QuerySelectMultipleField ('Coursework',
                query_factory=lambda: db.session.scalars(sqla.select(Coursework).order_by(Coursework.title)).all(),   
                get_label= lambda theCoursework : theCoursework.title,
                widget = ListWidget(prefix_label=False),
                option_widget=CheckboxInput())
    submit = SubmitField('Update')

        
    def validate_email(self, email):
        query = sqla.select(Student).where(Student.email == email.data)
        student = db.session.scalars(query).first()
        if student is not None:
            if student.id != current_user.id:
                raise ValidationError('The email already exists! Please use a different email.')
            

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')  

class SimpleNameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Save")

class CourseworkForm(FlaskForm):
    coursenum = StringField("Course Number", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    instructor = StringField("Instructor", validators=[DataRequired()])
    submit = SubmitField("Save")

class ApplicationForm(FlaskForm):
    statement = TextAreaField("Statement of Interest", validators=[DataRequired(), Length(max=2000)])
    reference_id = SelectField("Faculty Reference (if required)", coerce=int, validators=[Optional()])
    submit = SubmitField("Apply")

class SortForm(FlaskForm):
    sort_posts = SelectField(
        'Sort By Recommended',
        choices=[
           ('recommended', 'Recommended')
        ]  
    )
    my_posts_only = BooleanField('Display Recommended Posts:')
    submit = SubmitField('Sort')

    #sort by point system

    