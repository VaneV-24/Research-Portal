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
    tests = app.test_client()

    ctx = app.app_context()
    ctx.push()
    yield tests
    ctx.pop()


@pytest.fixture
def init_database():
    db.create_all()


    def test_password_hashing(self):
        u = User(firstname="Jake", lastname="Claybrook",
                 email="jake@wpi.edu", user_type="Student")
        u.set_password("12345")

        self.assertTrue(u.check_password("12345"))
        self.assertFalse(u.check_password("wrong"))

    def test_student_majors(self):
        s = Student(username="jake", firstname="Jake",
                    lastname="Claybrook", email="jake@wpi.edu", gpa=3.5)
        m1 = Major(name="RBE")
        m2 = Major(name="CS")

        db.session.add_all([s, m1, m2])
        db.session.commit()


        self.assertEqual(s.get_majors(), [])


        s.majors_of_student.extend([m1, m2])
        db.session.commit()

        majors = s.get_majors()
        self.assertEqual(len(majors), 2)
        self.assertEqual({m.name for m in majors}, {"RBE", "CS"})

   
    def test_position_fields(self):
        f = Faculty(username="prof", firstname="John",
                    lastname="Doe", email="prof@wpi.edu")
        db.session.add(f)
        db.session.commit()

        p = Positions(
            title="Research Assistant",
            body="Work on robotics.",
            startdate="2025",
            enddate="2026",
            team_size=3,
            min_gpa=3.0,
            reference_required=False,
            faculty_id=f.id
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.title, "Research Assistant")
        self.assertEqual(p.team_size, 3)
        self.assertEqual(p.min_gpa, 3.0)
        self.assertFalse(p.reference_required)
        self.assertEqual(p.faculty_id, f.id)


    def test_student_application_relationships(self):
        s = Student(username="s1", firstname="Jake", lastname="Claybrook",
                    email="s1@wpi.edu", gpa=3.6)
        f = Faculty(username="prof", firstname="John",
                    lastname="Doe", email="prof@wpi.edu")

        db.session.add_all([s, f])
        db.session.commit()

        p = Positions(
            title="RA", body="Research work.",
            startdate="2025", enddate="2026",
            team_size=2, min_gpa=3.0,
            reference_required=False,
            faculty_id=f.id
        )
        db.session.add(p)
        db.session.commit()

        a = Application(
            student_id=s.id,
            position_id=p.id,
            statement="I really want this position.",
            reference_id=f.id,
            status="Pending"
        )

        db.session.add(a)
        db.session.commit()

        self.assertEqual(len(s.applications), 1)
        self.assertEqual(s.applications[0].position_id, p.id)

        self.assertEqual(len(p.student_applications), 1)
        self.assertEqual(p.student_applications[0].student_id, s.id)


    def test_position_approved_count_and_capacity(self):
        f = Faculty(username="pf", firstname="John", lastname="Doe",
                    email="pf@wpi.edu")
        db.session.add(f)

        s1 = Student(username="s1", firstname="A", lastname="B",
                     email="s1@wpi.edu", gpa=3.8)
        s2 = Student(username="s2", firstname="C", lastname="D",
                     email="s2@wpi.edu", gpa=3.7)

        db.session.add_all([s1, s2])
        db.session.commit()

        p = Positions(
            title="Lab Position", body="Testing robots.",
            startdate="2025", enddate="2026",
            team_size=2, min_gpa=3.0,
            reference_required=False,
            faculty_id=f.id
        )
        db.session.add(p)
        db.session.commit()

        a1 = Application(student_id=s1.id, position_id=p.id,
                         statement="Hi", status="Approved")
        a2 = Application(student_id=s2.id, position_id=p.id,
                         statement="Hello", status="Pending")

        db.session.add_all([a1, a2])
        db.session.commit()

        self.assertEqual(p.approved_count(), 1)
        self.assertTrue(p.has_space())


        a2.status = "Approved"
        db.session.commit()

        self.assertEqual(p.approved_count(), 2)
        self.assertFalse(p.has_space())

    def test_gpa_requirement_enforced(self):
        f = Faculty(username="pf", firstname="John", lastname="Doe",
                    email="pf2@wpi.edu")
        db.session.add(f)
        db.session.commit()

        pos = Positions(
            title="High GPA Job",
            body="Hard work",
            startdate="2025",
            enddate="2026",
            team_size=1,
            min_gpa=3.5,
            reference_required=False,
            faculty_id=f.id
        )
        db.session.add(pos)
        db.session.commit()

        student_low = Student(username="low", firstname="Low",
                              lastname="GPA", email="low@wpi.edu", gpa=2.8)
        student_high = Student(username="high", firstname="High",
                               lastname="GPA", email="high@wpi.edu", gpa=3.8)

        db.session.add_all([student_low, student_high])
        db.session.commit()

    
        low_app = Application(
            student_id=student_low.id,
            position_id=pos.id,
            statement="Try",
            status="Pending"
        )
        high_app = Application(
            student_id=student_high.id,
            position_id=pos.id,
            statement="Qualified",
            status="Pending"
        )

        db.session.add_all([low_app, high_app])
        db.session.commit()

        self.assertTrue(student_high.gpa >= pos.min_gpa)
        self.assertFalse(student_low.gpa >= pos.min_gpa)

   
    def test_reference_requirement(self):
        f = Faculty(username="pf3", firstname="John", lastname="Doe",
                    email="pf3@wpi.edu")
        db.session.add(f)
        db.session.commit()

        pos = Positions(
            title="Ref Needed",
            body="Requires reference",
            startdate="2025",
            enddate="2026",
            team_size=1,
            min_gpa=3.0,
            reference_required=True,
            faculty_id=f.id
        )
        db.session.add(pos)
        db.session.commit()

        s = Student(username="stud", firstname="A", lastname="B",
                    email="stud@wpi.edu", gpa=3.6)
        db.session.add(s)
        db.session.commit()

        app_missing_ref = Application(
            student_id=s.id,
            position_id=pos.id,
            statement="Please",
            reference_id=None,
            status="Pending"
        )

        db.session.add(app_missing_ref)
        db.session.commit()

        # Logic test: reference required but not supplied
        self.assertTrue(pos.reference_required)
        self.assertIsNone(app_missing_ref.reference_id)