from app import create_app, db
from config import Config
from app.main.models import Major, Student, Topic, Coursework, Languages, Faculty, Positions, Application
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from faculty_data import faculty


app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {
        'sqla': sqla, 
        'sqlo': sqlo,
        'db': db,
        'Major': Major,
        'Student': Student,
        'Topic': Topic,
        'Languages': Languages,
        'Coursework': Coursework,
        'Faculty': Faculty,
        'Application': Application
    }

@sqla.event.listens_for(Faculty.__table__, 'after_create')
def add_faculty_members(*args, **kwargs): 
    query = sqla.select(Faculty)
    if db.session.scalars(query).first() is None:
        for f in faculty:
            db.session.add(Faculty(username = None, password_hash = None, firstname = f['firstname'], lastname = f['lastname'], email = f['email']))
        db.session.commit()

def seed_majors():
    if db.session.query(Major).first() is None:
        majors = ["CS", "DS", "RBE", "ME", "MATH"]
        for m in majors:
            db.session.add(Major(name=m))
        db.session.commit()

def seed_topics():
    if db.session.query(Topic).first() is None:
        topics = [
            "Machine Learning",
            "Computing",
            "Prototyping",
            "Programming",
            "Testing"
        ]
        for t in topics:
            db.session.add(Topic(name=t))
        db.session.commit()

def seed_languages():
    if db.session.query(Languages).first() is None:
        langs = ["Racket", "C++", "Python", "C", "JavaScript"]
        for l in langs:
            db.session.add(Languages(name=l))
        db.session.commit()

def seed_coursework():
    if db.session.query(Coursework).first() is None:
        courseworks = [
            {"coursenum": "CS101", "title": "Intro to CS"},
            {"coursenum": "CS102", "title": "Data Structures"},
            {"coursenum": "CS201", "title": "Algorithms"},
            {"coursenum": "CS301", "title": "Operating Systems"},
            {"coursenum": "ME101", "title": "Robotics"},
            {"coursenum": "CS202", "title": "Databases"}
        ]
        for c in courseworks:
            db.session.add(Coursework(
                coursenum=c["coursenum"],
                title=c["title"],
                grade="N/A",        # default placeholder
                instructor="TBD"    # default placeholder
            ))
        db.session.commit()
        print("Coursework seeded!")

def seed_positions():
    # only seed if empty
    if Positions.query.first() is not None:
        print("Position already exists — skipping seed.")
        return

    # --- OPTIONAL: fetch related objects ---
    topics = Topic.query.all()
    majors = Major.query.all()
    languages = Languages.query.all()
    coursework = Coursework.query.all()

    # --- Position 1 ---
    r1 = Positions(
        title="AI Robotics Navigation",
        body="Research project on autonomous robot navigation using computer vision.",
        startdate="2025-01-01",
        enddate="2025-06-01",
        team_size=4,
        min_gpa=3.0,
        faculty_id=3,
        reference_required=False
    )
    r1.topics_positions = topics[:2]          
    r1.majors_positions = majors[:1]          
    r1.languages_positions = languages[:2]    
    r1.coursework_positions = coursework[:3]  

    # --- Position 2 ---
    r2 = Positions(
        title="Brain-Computer Interface Design",
        body="Assist in developing BCI hardware and software for signal processing.",
        startdate="2025-02-01",
        enddate="2025-12-01",
        team_size=3,
        min_gpa=3.2,
        faculty_id=6,
        reference_required=True
    )
    r2.topics_positions = topics[1:3]
    r2.majors_positions = majors[:2]
    r2.languages_positions = languages[:1]
    r2.coursework_positions = coursework[2:5]

    db.session.add(r1)
    db.session.add(r2)
    db.session.commit()
    print("Position opportunities seeded!")

def init_db():
    """Create all tables and seed them if empty."""
    db.create_all()
    seed_majors()
    seed_topics()
    seed_languages()
    seed_coursework()
    seed_positions()

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
