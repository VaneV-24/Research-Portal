from app import db, oauth
from flask import render_template, flash, redirect, url_for, current_app, request, session
import requests
import sqlalchemy as sqla

from app.main.models import Student, Faculty, User, StudentCoursework
from app.auth.auth_forms import RegistrationForm, LoginForm, FacultyRegistrationForm

from flask_login import current_user, login_user, logout_user, login_required
from app.auth import auth_blueprint as auth
from os import environ as env
from urllib.parse import quote_plus, urlencode

# Email support
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer

def generate_token(email):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="email-verify")


def confirm_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="email-verify", max_age=expiration)
    except:
        return False
    return email


def send_email(to_email, subject, html_body, plain_body=None):
    email_user = "youbetternotreply.untitled@gmail.com"
    email_pass = "qlgj iicd mvgm xoqm"

    msg = MIMEMultipart("alternative")
    msg["From"] = email_user
    msg["To"] = to_email
    msg["Subject"] = subject

    part_plain = MIMEText(plain_body, "plain")
    part_html = MIMEText(html_body.lstrip(), "html")
    msg.attach(part_plain)
    msg.attach(part_html)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_user, email_pass)
        server.send_message(msg)

    print("Email sent!")

def create_auth0_user(email, password, name):
    """Create user in Auth0 database"""
    response = None
    try:
        # Get Management API token
        token_url = f"https://{current_app.config['AUTH0_DOMAIN']}/oauth/token"
        token_payload = {
            "client_id": current_app.config['AUTH0_CLIENT_ID'],
            "client_secret": current_app.config['AUTH0_CLIENT_SECRET'],
            "audience": f"https://{current_app.config['AUTH0_DOMAIN']}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        token_response = requests.post(token_url, json=token_payload)

        access_token = token_response.json()['access_token']
        
        
        # Create user
        users_url = f"https://{current_app.config['AUTH0_DOMAIN']}/api/v2/users"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data = {
            "email": email,
            "password": password,
            "connection": "Username-Password-Authentication",  # Your database connection name
            "name": name,
            "email_verified": False  # Set to True if already verified in your system
        }
        
        response = requests.post(users_url, json=user_data, headers=headers)
        print("AUTH0 CREATE USER RESPONSE:", response.status_code, response.text)
        return response.json()
        
    except Exception as e:
        print(f"Error creating Auth0 user: {e}")
        # Don't fail registration if Auth0 sync fails
        return None

# ---------------- USER ROUTES ----------------
@auth.route('/user/login', methods =['GET','POST'])
def login():
    if current_user.is_authenticated:
        if current_user.user_type == "Student":
            return redirect(url_for('main.student_index'))
        else:
            return redirect(url_for('main.faculty_index'))
    lform = LoginForm()
    if lform.validate_on_submit():
        user = db.session.scalars(sqla.select(User).where(
            User.email == lform.email.data)).first()
        if(user is None) or (user.check_password(lform.password.data) == False):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember = lform.remember_me.data)
        if current_user.user_type=="Student":
            flash(f'The user {current_user.username} has successfully logged in!')
            return redirect(url_for('main.student_index'))
        else:
            flash(f'The user {current_user.username} has successfully logged in!')
            return redirect(url_for('main.faculty_index'))
    return render_template('login.html', title = 'Sign In', form=lform)

@auth.route('/user/logout')
@login_required
def logout_users():
    logout_user()
    if 'user' in session:
        return redirect(url_for('sso_logout'))
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))

@auth.route('/user/ssologin')
def ssologin():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for('auth.callback', _external=True),
        prompt='login'
    )

@auth.route('/callback', methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["auth0_user"] = token

        user_info = token.get('userinfo')
        email = user_info.get('email')

        session_user = User.query.filter_by(email=email).first()

        if session_user is not None:
            login_user(session_user)
            if isinstance(session_user, Student):
                flash(f'SSO login successful for: Username - {session_user.username}, Email - {session_user.email}')
                return redirect(url_for('main.student_index'))
            
            elif isinstance(session_user, Faculty):
                if session_user.verified:
                    flash(f'SSO login successful for: Username - {session_user.username}, Email - {session_user.email}')
                    return redirect(url_for('main.faculty_index'))
                return redirect(url_for('auth.login'))
        
        flash("Sorry, that user does not exist! Please register first!")
        return redirect(url_for('auth.login'))
    except Exception as e:
        print(f"OAuth Error: {e}")
        flash('Login failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

@auth.route("/user/ssologout")
@login_required
def ssologout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("main.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# ---------------- STUDENT ROUTES ----------------
@auth.route('/student/register', methods=['GET', 'POST'])
def register_student():
    rform = RegistrationForm()
    if rform.validate_on_submit():
        selected_coursework = rform.coursework_students.data
        
        missing_grades = []
        
        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            if not grade or grade == "":
                missing_grades.append(coursework.title)
        
        if missing_grades:
            flash(f'Please provide grades for: {", ".join(missing_grades)}', 'danger')
            return render_template('register_student.html', form=rform)
        
        student = Student(
            username=rform.username.data,
            firstname=rform.firstname.data,
            lastname=rform.lastname.data,
            email=rform.email.data,
            gpa=rform.gpa.data
        )
        student.set_password(rform.password.data)

        student.topics_students = rform.topics_students.data
        student.majors_of_student = rform.majors_of_student.data
        student.languages_students = rform.languages_students.data

        db.session.add(student)
        create_auth0_user( email=rform.email.data, 
                          password=rform.password.data, 
                          name=f"{rform.firstname.data} {rform.lastname.data}" )
        db.session.flush()

        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            student_coursework = StudentCoursework(
                student=student,
                coursework=coursework,
                grade=grade
            )
            db.session.add(student_coursework)
        
        db.session.add(student)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    else:
        print(rform.form_errors)
    
    return render_template('register_student.html', form=rform)

# ---------------- FACULTY ROUTES ----------------
@auth.route("/faculty/register", methods=["GET", "POST"])
def register_faculty():
    rform = FacultyRegistrationForm()
    if rform.validate_on_submit():
        faculty_entry = Faculty.query.filter_by(email=rform.email.data).first()
        if (faculty_entry is None):
            flash('Faculty does not exist!')
            return redirect(url_for('auth.login'))
        faculty_entry.username = rform.username.data
        faculty_entry.set_password(rform.password.data)
        db.session.commit()
        db.session.refresh(faculty_entry)
        token = generate_token(faculty_entry.email)
        verify_url = url_for("auth.verify_email", token=token, _external=True)
        html_body = f"""<html>
        <body>
        <p>Hello {faculty_entry.firstname},</p>\

        <p>Click the link below to verify your faculty account:</p>\

        <p>
            <a href="{verify_url}" style="font-size:16px;">
                Verify Faculty Account
            </a>
        </p>\

        <p>If the link doesn't work, copy and paste this URL into your browser:</p>
        <p>{verify_url}</p>\

        <p> This link expires in 1 hour. </p>
        </body>
        </html>
        """
        plain_body = f"Please verify your faculty account: {verify_url}"
        send_email(faculty_entry.email, "Verify Your Account", html_body, plain_body)
        flash("Faculty registration successful! Check your email for verification.")
        return redirect(url_for('auth.login'))
    return render_template('register_faculty.html', form=rform)

# ---------------- EMAIL VERIFICATION ----------------
@auth.route("/verify/<token>")
def verify_email(token):
    email = confirm_token(token)
    if not email:
        return "Verification link is invalid or expired.", 400

    user = Faculty.query.filter_by(email=email).first()
    if not user:
        return "No user found for this email.", 404

    if user.verified:
        return "Email already verified."

    user.verified = True
    db.session.commit()
    flash("Email verified successfully!")
    return redirect(url_for('auth.login'))
