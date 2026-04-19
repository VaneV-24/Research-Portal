from app import db
from flask import render_template, flash, redirect, url_for, request, session
from flask import render_template, flash, redirect, url_for, request, session
import sqlalchemy as sqla
from app.main.models import Student, Major, Languages, Coursework, Topic, Positions, Faculty, Application, StudentCoursework
from app.main.models import Student, Major, Languages, Coursework, Topic, Positions, Faculty, Application, StudentCoursework
from app.main.forms import EditStudentForm, EmptyForm, PositionsForm, SimpleNameForm, CourseworkForm, ApplicationForm
from flask_login import current_user, login_required
from sqlalchemy import text
from functools import wraps

from functools import wraps

from app.main import main_blueprint as main

#------------------ USER DECORATORS ------------------#
def student_required(func):
    @wraps(func)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.user_type == 'Student':
            flash("You must be a student to access this page.")
            return redirect(url_for("main.home"))
        return func(*args, **kwargs)
    return decorated


def faculty_required(func):
    @wraps(func)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.user_type != 'Faculty':
            flash("You must be faculty to access this page.")
            return redirect(url_for("main.home"))

        if not current_user.verified:
            flash("Your faculty account is not verified yet!")
            return redirect(url_for("auth.logout_users"))
        return func(*args, **kwargs)
    return decorated


@main.route('/', methods=['GET'])
@main.route('/home', methods=['GET'])
def home():
    positions = Positions.query.all()
    num_positions = len(positions)
    return render_template(
        "home.html",
        positions=positions,
        num_positions=num_positions)

@main.route("/user/position/<int:id>/view")
@login_required
def view_position(id):
    position = Positions.query.get_or_404(id)
    return render_template("view_research.html", position=position)

# ---------------- STUDENT ROUTES ----------------
@main.route('/student/index', methods=['GET', 'POST'])
@student_required
def student_index():
    empty_form = EmptyForm()
    student = current_user  

    positions = Positions.query.all()
    num_positions = len(positions)

    def score_position_for_student(position, student):
        score = 0

        # Major score
        student_majors = {m.id for m in student.majors_of_student}
        position_majors = {m.id for m in position.majors_positions}
        score += len(student_majors.intersection(position_majors)) * 3

        # Topic score
        student_topics = {t.id for t in student.topics_students}
        position_topics = {t.id for t in position.topics_positions}
        score += len(student_topics.intersection(position_topics)) * 2

        # Coursework score (FIXED)
        student_courses = {sc.coursework_id for sc in student.coursework_students}
        position_courses = {c.id for c in position.coursework_positions}
        score += len(student_courses.intersection(position_courses)) * 1

        return score

    scored_positions = [
        (position, score_position_for_student(position, student))
        for position in positions
    ]

    scored_positions.sort(key=lambda x: x[1], reverse=True)

    recommended_positions = [p for p, s in scored_positions[:3] if s > 0]

    recommended_ids = {p.id for p in recommended_positions}
    other_positions = [p for p, s in scored_positions if p.id not in recommended_ids]

    return render_template(
        "student_index.html",
        num_positions=num_positions,
        form=empty_form,
        recommended_positions=recommended_positions,
        other_positions=other_positions
    )


@main.route('/student/profile', methods = ['GET'])
@student_required
def display_student_profile():
     empty_form = EmptyForm()
     return render_template('display_student_profile.html', 
                            title = 'Display Profile', 
                            student = current_user, 
                            form = empty_form,
                            session=session.get("user"))

@main.route('/student/editprofile', methods=['GET', 'POST'])
@student_required
def edit_student_profile():
    eform = EditStudentForm()

    if request.method == 'POST' and eform.validate_on_submit():
        selected_coursework = eform.coursework.data
        
        missing_grades = []
        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            if not grade or grade == "":
                missing_grades.append(coursework.title)
        
        if missing_grades:
            flash(f'Please provide grades for: {", ".join(missing_grades)}', 'danger')
            # Pass existing grades when re-rendering
            existing_grades = {sc.coursework_id: sc.grade for sc in current_user.student_coursework}
            return render_template('edit_student_profile.html', title='Edit Profile', form=eform, existing_grades=existing_grades)
        
        selected_coursework = eform.coursework.data
        
        missing_grades = []
        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            if not grade or grade == "":
                missing_grades.append(coursework.title)
        
        if missing_grades:
            flash(f'Please provide grades for: {", ".join(missing_grades)}', 'danger')
            # Pass existing grades when re-rendering
            existing_grades = {sc.coursework_id: sc.grade for sc in current_user.student_coursework}
            return render_template('edit_student_profile.html', title='Edit Profile', form=eform, existing_grades=existing_grades)
        
        current_user.username = eform.username.data
        current_user.firstname = eform.firstname.data
        current_user.lastname = eform.lastname.data
        current_user.email = eform.email.data
        current_user.gpa = eform.gpa.data

        if eform.password.data:
            current_user.set_password(eform.password.data)

        current_user.majors_of_student.clear()
        for m in eform.majors.data:
            current_user.majors_of_student.append(m)

        current_user.topics_students.clear()
        for t in eform.topics.data:
            current_user.topics_students.append(t)

        current_user.languages_students.clear()
        for l in eform.languages.data:
            current_user.languages_students.append(l)

        StudentCoursework.query.filter_by(student_id=current_user.id).delete()
        
        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            student_coursework = StudentCoursework(
                student_id=current_user.id,
                coursework_id=coursework.id,
                grade=grade
            )
            db.session.add(student_coursework)
        StudentCoursework.query.filter_by(student_id=current_user.id).delete()
        
        for coursework in selected_coursework:
            grade_key = f'grade_{coursework.id}'
            grade = request.form.get(grade_key)
            
            student_coursework = StudentCoursework(
                student_id=current_user.id,
                coursework_id=coursework.id,
                grade=grade
            )
            db.session.add(student_coursework)

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.display_student_profile'))

    elif request.method == 'GET':
        eform.username.data = current_user.username
        eform.firstname.data = current_user.firstname
        eform.lastname.data = current_user.lastname
        eform.email.data = current_user.email
        eform.gpa.data = current_user.gpa

        eform.majors.data = current_user.majors_of_student
        eform.topics.data = current_user.topics_students
        eform.languages.data = current_user.languages_students
        eform.coursework.data = [course.coursework for course in current_user.coursework_students]
        
        # Build existing grades dictionary and pass to template
        existing_grades = {sc.coursework_id: sc.grade for sc in current_user.coursework_students}


    return render_template('edit_student_profile.html', title = 'Edit Profile', form = eform, existing_grades=existing_grades)

@main.route("/student/dashboard")
@student_required
def student_dashboard():
    apps = Application.query.filter_by(student_id=current_user.id).all()
    return render_template("student_dashboard.html", apps=apps)
@main.route("/student/position/<position_id>/apply", methods=["GET", "POST"])
@student_required
def apply_to_position(position_id):
    position = Positions.query.get_or_404(position_id)
    form = ApplicationForm()

    if position.reference_required:
        faculty_list = Faculty.query.filter_by(verified=True).all()
        form.reference_id.choices = [
            (f.id, f"{f.firstname} {f.lastname}") for f in faculty_list
        ]
    else:
        form.reference_id.choices = [(0, "None")]
    if position.reference_required:
        faculty_list = Faculty.query.filter_by(verified=True).all()
        form.reference_id.choices = [
            (f.id, f"{f.firstname} {f.lastname}") for f in faculty_list
        ]
    else:
        form.reference_id.choices = [(0, "None")]

    if form.validate_on_submit():

        if position.reference_required and not form.reference_id.data:
            flash("This research position requires selecting a faculty reference.")
            return render_template("application.html", form=form, position=position)

        if position.reference_required:
            ref_id = form.reference_id.data
        else:
            ref_id = None if form.reference_id.data == 0 else form.reference_id.data

        new_application = Application(
            statement=form.statement.data,
            student_id=current_user.id,
            position_id=position.id,
            reference_id=ref_id
        )

        db.session.add(new_application)
        db.session.commit()


        flash("Application submitted successfully!", "success")
        return redirect(url_for("main.student_index"))

    return render_template("application.html", form=form, position=position)

@main.route('/withdraw_application/<int:app_id>', methods=['POST'])
@student_required
def withdraw_application(app_id):
    app = Application.query.get_or_404(app_id)

    # Safety: ensure student owns this application
    if app.student_id != current_user.id:
        flash("You cannot withdraw an application that is not yours.", "danger")
        return redirect(url_for('main.student_dashboard'))

    # Cannot withdraw approved applications
    if app.status == "Approved":
        flash("You cannot withdraw an approved application.", "danger")
        return redirect(url_for('main.student_dashboard'))

    # Withdraw only allowed for Pending
    if app.status == "Pending":
        db.session.delete(app)
        db.session.commit()
        flash("Your application has been withdrawn.", "success")

    return redirect(url_for('main.student_dashboard'))
# ---------------- FACULTY ROUTES ----------------
@main.route('/faculty/index', methods=['GET', 'POST'])
@faculty_required
def faculty_index():
    empty_form = EmptyForm()
    faculties = db.session.scalars(sqla.select(Faculty))   
    positions = db.session.scalars(current_user.user_positions()).all()
    applicants_by_position = {}
    applications_by_position = {}
    application_statuses = {}

    for position in positions:
        apps = db.session.scalars(
            sqla.select(Application).where(
                Application.position_id == position.id)).all()

        application_statuses[position.id] = {
            app.student_id: app.status for app in apps
        }
        
        applications_by_position[position.id] = {
            app.student_id: app.id for app in apps
        }

        student_ids = {app.student_id for app in apps}

        students = db.session.scalars(
            sqla.select(Student).where(
                Student.id.in_(student_ids))).all()

        applicants_by_position[position.id] = students
    num_positions = len(positions)
    return render_template("faculty_index.html",
                            positions=positions,
                            num_positions=num_positions, faculties = faculties,
                            applicants_by_position=applicants_by_position,
                            applications_by_position=applications_by_position,
                            application_statuses=application_statuses, 
                            form = empty_form)

@main.route('/faculty/profile', methods = ['GET'])
@faculty_required
def display_faculty_profile():
    empty_form = EmptyForm()
    positions = db.session.scalars(current_user.user_positions()).all()
    
    reference_requests = db.session.scalars(
    sqla.select(Application).where(
        Application.reference_id == current_user.id)).all()

    reference_data = []
    for app in reference_requests:
        reference_data.append({
            "application_id": app.id,
            "student": db.session.get(Student, app.student_id),
            "position": db.session.get(Positions, app.position_id),
            "status": app.reference_status
        })

    return render_template('display_faculty_profile.html', 
                            positions=positions, 
                            faculty = current_user, 
                            form = empty_form,
                            reference_data=reference_data)

@main.route('/faculty/position/post', methods=['GET', 'POST'])
@faculty_required
def post_position():
    pform = PositionsForm()
    if pform.validate_on_submit():
        position = Positions(title = pform.title.data,
                    body = pform.body.data ,
                    startdate = pform.startdate.data,
                    enddate = pform.enddate.data,
                    team_size = pform.team_size.data,
                    min_gpa = pform.min_gpa.data,
                    reference_required = pform.reference_required.data)
        
        position.faculty_id = current_user.id
        position.majors_positions = pform.majors_of_position.data
        position.topics_positions = pform.topics_position.data
        position.coursework_positions = pform.coursework_position.data
        position.languages_positions = pform.languages_position.data
        db.session.add(position)
        db.session.commit()
        flash('Congratulations, your Position Opportunity has been created')
        return redirect(url_for('main.faculty_index'))

    return render_template('_createpositions.html', form = pform)

@main.route("/faculty/lists")
@faculty_required
def faculty_lists():
    return render_template("faculty_lists.html")

@main.route("/faculty/majors")
@faculty_required
def faculty_majors():
    majors = Major.query.order_by(Major.name).all()
    return render_template("faculty_majors.html", majors=majors)

@main.route("/faculty/majors/add", methods=["GET", "POST"])
@faculty_required
def add_major():
    form = SimpleNameForm()
    if form.validate_on_submit():
        db.session.add(Major(name=form.name.data))
        db.session.commit()
        return redirect(url_for("main.faculty_majors"))
    return render_template("faculty_edit_item.html", form=form, title="Add Major")

@main.route("/faculty/majors/<major_id>/edit", methods=["GET", "POST"])
@faculty_required
def edit_major(major_id):
    major = Major.query.get_or_404(major_id)
    form = SimpleNameForm(obj=major)
    if form.validate_on_submit():
        major.name = form.name.data
        db.session.commit()
        return redirect(url_for("main.faculty_majors"))
    return render_template("faculty_edit_item.html", form=form, title="Edit Major")

@main.route("/faculty/majors/<major_id>/delete")
@faculty_required
def delete_major(major_id):
    major = Major.query.get_or_404(major_id)
    db.session.delete(major)
    db.session.commit()
    return redirect(url_for("main.faculty_majors"))

@main.route("/faculty/topics")
@faculty_required
def faculty_topics():
    topics = Topic.query.order_by(Topic.name).all()
    return render_template("faculty_topics.html", topics=topics)

@main.route("/faculty/topics/add", methods=["GET", "POST"])
@faculty_required
def add_topic():
    form = SimpleNameForm()
    if form.validate_on_submit():
        db.session.add(Topic(name=form.name.data))
        db.session.commit()
        return redirect(url_for("main.faculty_topics"))
    return render_template("faculty_edit_item.html", form=form, title="Add Topic")

@main.route("/faculty/topics/<topic_id>/edit", methods=["GET", "POST"])
@faculty_required
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    form = SimpleNameForm(obj=topic)
    if form.validate_on_submit():
        topic.name = form.name.data
        db.session.commit()
        return redirect(url_for("main.faculty_topics"))
    return render_template("faculty_edit_item.html", form=form, title="Edit Topic")

@main.route("/faculty/topics/<topic_id>/delete")
@faculty_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    return redirect(url_for("main.faculty_topics"))

@main.route("/faculty/languages")
@faculty_required
def faculty_languages():
    langs = Languages.query.order_by(Languages.name).all()
    return render_template("faculty_languages.html", langs=langs)

@main.route("/faculty/languages/add", methods=["GET", "POST"])
@faculty_required
def add_language():
    form = SimpleNameForm()
    if form.validate_on_submit():
        db.session.add(Languages(name=form.name.data))
        db.session.commit()
        return redirect(url_for("main.faculty_languages"))
    return render_template("faculty_edit_item.html", form=form, title="Add Language")

@main.route("/faculty/languages/<languages_id>/edit", methods=["GET", "POST"])
@faculty_required
def edit_language(languages_id):
    language = Languages.query.get_or_404(languages_id)
    form = SimpleNameForm(obj=language)
    if form.validate_on_submit():
        language.name = form.name.data
        db.session.commit()
        return redirect(url_for("main.faculty_languages"))
    return render_template("faculty_edit_item.html", form=form, title="Edit Language")

@main.route("/faculty/languages/<languages_id>/delete")
@faculty_required
def delete_language(languages_id):
    language = Languages.query.get_or_404(languages_id)
    db.session.delete(language)
    db.session.commit()
    return redirect(url_for("main.faculty_languages"))

@main.route("/faculty/coursework")
@faculty_required
def faculty_coursework():
    items = Coursework.query.order_by(Coursework.coursenum).all()
    return render_template("faculty_coursework.html", items=items)

@main.route("/faculty/coursework/add", methods=["GET", "POST"])
@faculty_required
def add_coursework():
    form = CourseworkForm()
    if form.validate_on_submit():
        c = Coursework(
            coursenum=form.coursenum.data,
            title=form.title.data,
            instructor=form.instructor.data
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for("main.faculty_coursework"))
    else:
        print(form.errors)
    return render_template("faculty_edit_item.html", form=form, title="Add Coursework")

@main.route("/faculty/coursework/<coursework_id>/edit", methods=["GET", "POST"])
@faculty_required
def edit_coursework(coursework_id):
    c = Coursework.query.get_or_404(coursework_id)
    form = CourseworkForm(obj=c)
    if form.validate_on_submit():
        c.coursenum = form.coursenum.data
        c.title = form.title.data
        db.session.commit()
        return redirect(url_for("main.faculty_coursework"))
    return render_template("faculty_edit_item.html", form=form, title="Edit Coursework")

@main.route("/faculty/coursework/<coursework_id>/delete")
@faculty_required
def delete_coursework(coursework_id):
    c = Coursework.query.get_or_404(coursework_id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for("main.admin_coursework"))

@main.route("/faculty/application/<application_id>/approve", methods=['POST'])
@faculty_required
def approve_application(application_id):
    app = db.session.get(Application, application_id)
    if app is not None:
        position = app.position
        if position.faculty_id != current_user.id:
            flash('Sorry! You can not approve this application because you did not create this position')
            return redirect(url_for('main.faculty_index'))
        if not position.has_space():
            flash('Sorry! You have reached the maximum number of approved students for this position')
            return redirect(url_for('main.faculty_index'))
        if app.status == "Approved":
            flash("This application is already approved.")
            return redirect(url_for('main.faculty_index'))
        app.status = "Approved"
        db.session.commit()
        flash("Application approved.")

    return redirect(url_for('main.faculty_index'))

@main.route("/faculty/application/<application_id>/reject", methods=["POST"])
@faculty_required
def reject_application(application_id):
    app = db.session.get(Application, application_id)
    if app is not None:
        position = app.position
        if position.faculty_id != current_user.id:
            flash('Sorry! You can not reject this application because you did not create this position')
            return redirect(url_for('main.faculty_index'))

        app.status = "Rejected"
        db.session.commit()

    flash("Application rejected.")
    return redirect(url_for('main.faculty_index'))

@main.route("/faculty/application/view/<student_id>/<application_id>", methods=['GET'])
@faculty_required
def view_student(student_id, application_id):
    student = db.session.get(Student, student_id)

    if student is None:
        flash("Student not found!")
        return redirect(url_for("main.display_faculty_profile"))
    
    application = db.session.get(Application, application_id)
    if application is None or application.student_id != int(student_id):
        flash("Application not found!")
        return redirect(url_for("main.display_faculty_profile"))
    
    return render_template(
        "view_student.html",
        student=student,
        application=application
    )
@main.route("/faculty/application/<application_id>/recommended", methods=["POST"])
@faculty_required
def recommend_student(application_id):
    app = db.session.get(Application, application_id)

    if app is None:
        flash("Application not found.")
        return redirect(url_for("main.display_faculty_profile"))

    # Ensure faculty is the reference for this application
    if app.reference_id != current_user.id:
        flash("You are not authorized to modify this reference request.")
        return redirect(url_for("main.display_faculty_profile"))

    app.reference_status = "Recommended"
    db.session.commit()

    flash("You have recommended this student.")
    return redirect(url_for("main.display_faculty_profile", app_id=application_id))

@main.route("/application/<application_id>/notrecommended", methods=["POST"])
@faculty_required
def not_recommend_student(application_id):
    app = db.session.get(Application, application_id)

    if app is None:
        flash("Application not found.")
        return redirect(url_for("main.display_faculty_profile"))

    # Ensure faculty owns this reference
    if app.reference_id != current_user.id:
        flash("You are not authorized to modify this reference request.")
        return redirect(url_for("main.display_faculty_profile"))

    app.reference_status = "Not Recommended"
    db.session.commit()

    flash("You have declined this recommendation.")
    return redirect(url_for("main.display_faculty_profile", app_id=application_id))