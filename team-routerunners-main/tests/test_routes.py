import pytest
import sqlalchemy as sqla
from app import create_app, db
from config import Config
from app.main.models import (
    User, Student, Faculty, Major, Positions, Application
)


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-key"



@pytest.fixture(scope="module")
def test_client():
    app = create_app(config_class=TestConfig)
    client = app.test_client()

    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture
def init_database():
    db.create_all()

   
    student = Student(
        username="jdoe",
        firstname="John",
        lastname="Doe",
        email="jdoe@wpi.edu",
        gpa="3.60",
        user_type="Student",
    )
    student.set_password("password123")

    faculty = Faculty(
        username="drsmith",
        firstname="Alice",
        lastname="Smith",
        email="asmith@wpi.edu",
        user_type="Faculty",
        verified=True
    )
    faculty.set_password("securepass")

    major = Major(name="Computer Science")

    position = Positions(
        title="Research Assistant – Robotics Lab",
        body="Assist with SLAM, ROS2, and mapping experiments.",
        startdate="2025-01-01",
        enddate="2025-12-31",
        team_size=2,
        min_gpa=3.2,
        reference_required=False,
        faculty=faculty,
    )

    # Link position to major
    position.majors_positions.append(major)

    db.session.add_all([student, faculty, major, position])
    db.session.commit()

    yield
    db.drop_all()


def login(test_client, email, password):
    response = test_client.post(
        "/user/login",
        data={"email": email, "password": password, "remember_me": False},
        follow_redirects=True,
    )
    assert response.status_code == 200

def logout(test_client):
    response = test_client.get("/user/logout",                       
                          follow_redirects = True)
    assert response.status_code == 200
    
def get_user(email):
    return db.session.scalars(
        sqla.select(User).where(User.email == email)
    ).first()


def get_position(title):
    return db.session.scalars(
        sqla.select(Positions).where(Positions.title == title)
    ).first()


# ---------------------------------------------------------------
# ROUTE TESTS
# ---------------------------------------------------------------

def test_homepage(test_client, init_database):
    r = test_client.get("/")
    assert r.status_code == 200
    assert b"Research" in r.data
    assert b"positions" in r.data.lower()


def test_view_position(test_client, init_database):
    login(test_client, "jdoe@wpi.edu", "password123")
    pos = get_position("Research Assistant – Robotics Lab")

    r = test_client.get(f"/user/position/{pos.id}/view")
    assert r.status_code == 200
    assert b"Robotics Lab" in r.data
    assert b"SLAM" in r.data  # body text check
    logout(test_client)


def test_student_index(test_client, init_database):
    login(test_client, "jdoe@wpi.edu", "password123")

    r = test_client.get("/student/index")
    assert r.status_code == 200
    assert b"Recommended For You" in r.data
    logout(test_client)


def test_student_profile(test_client, init_database):
    login(test_client, "jdoe@wpi.edu", "password123")

    r = test_client.get("/student/profile")
    assert r.status_code == 200
    assert b"John Doe" in r.data
    assert b"3.60" in r.data  # GPA visible
    logout(test_client)


def test_apply_to_position_get(test_client, init_database):
    login(test_client, "jdoe@wpi.edu", "password123")
    pos = get_position("Research Assistant – Robotics Lab")

    r = test_client.get(f"/student/position/{pos.id}/apply")
    assert r.status_code == 200
    assert b"Apply" in r.data
    html = r.data.decode('utf-8')
    assert "Research Assistant – Robotics Lab" in html
    logout(test_client)


def test_apply_to_position_post(test_client, init_database):
    login(test_client, "jdoe@wpi.edu", "password123")
    student = get_user("jdoe@wpi.edu")
    pos = get_position("Research Assistant – Robotics Lab")

    r = test_client.post(
        f"/student/position/{pos.id}/apply",
        data={"statement": "I want to work on SLAM.", "reference_id": 0},
        follow_redirects=True,
    )

    assert r.status_code == 200
    assert b"Application submitted" in r.data

    app = db.session.scalars(
        sqla.select(Application)
        .where(Application.student_id == student.id)
        .where(Application.position_id == pos.id)
    ).first()

    assert app is not None
    assert app.statement == "I want to work on SLAM."
    assert app.status == "Pending"
    logout(test_client)

def test_faculty_index(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.get("/faculty/index")
    assert r.status_code == 200
    assert b"positions" in r.data.lower()
    assert b"Robotics Lab" in r.data
    logout(test_client)


def test_faculty_profile(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.get("/faculty/profile")
    assert r.status_code == 200
    assert b"Reference Requests" in r.data
    assert b"Alice Smith" in r.data
    logout(test_client)


def test_faculty_add_major(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.post(
        "/faculty/majors/add",
        data={"name": "Data Science"},
        follow_redirects=True
    )

    assert r.status_code == 200

    added_major = db.session.scalars(
        sqla.select(Major).where(Major.name == "Data Science")
    ).first()

    assert added_major is not None
    logout(test_client)


def test_faculty_major_page(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.get("/faculty/majors")
    assert r.status_code == 200
    assert b"Computer Science" in r.data
    logout(test_client)


def test_faculty_lists(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.get("/faculty/lists")
    assert r.status_code == 200
    assert b"Faculty: Manage Predefined Lists" in r.data
    logout(test_client)


def test_post_position(test_client, init_database):
    login(test_client, "asmith@wpi.edu", "securepass")

    r = test_client.post(
        "/faculty/position/post",
        data={
            "title": "AI Research Intern",
            "body": "LLM safety and robotics alignment.",
            "startdate": "2025-03-01",
            "enddate": "2025-06-01",
            "team_size": 1,
            "min_gpa": 3.5,
            "reference_required": True,
        },
        follow_redirects=True
    )

    assert r.status_code == 200

    pos = get_position("AI Research Intern")
    assert pos is not None
    assert pos.min_gpa == 3.5
    assert pos.reference_required is True
    logout(test_client)