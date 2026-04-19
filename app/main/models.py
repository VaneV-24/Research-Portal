from typing import Optional
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#------------------ User Loader ------------------#
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

#------------------ Association Tables ------------------#
student_majors_table = db.Table(
    'students_majors_table',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True)
)
student_topics_table = db.Table(
    'student_topics_table',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('topic_id', sqla.Integer, sqla.ForeignKey('topic.id'), primary_key=True)
)
student_languages_table = db.Table(
    'student_languages_table',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('languages_id', sqla.Integer, sqla.ForeignKey('languages.id'), primary_key=True)
)
# student_coursework_table = db.Table(
#     'student_coursework_table',
#     db.metadata,
#     sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
#     sqla.Column('coursework_id', sqla.Integer, sqla.ForeignKey('coursework.id'), primary_key=True)
# )

positions_majors_table = db.Table(
    'positions_majors_table',
    db.metadata,
    sqla.Column('positions_id', sqla.Integer, sqla.ForeignKey('positions.id'), primary_key=True),
    sqla.Column('major_id', sqla.Integer, sqla.ForeignKey('major.id'), primary_key=True)
)
positions_topics_table = db.Table(
    'positions_topics_table',
    db.metadata,
    sqla.Column('positions_id', sqla.Integer, sqla.ForeignKey('positions.id'), primary_key=True),
    sqla.Column('topic_id', sqla.Integer, sqla.ForeignKey('topic.id'), primary_key=True)
)
positions_languages_table = db.Table(
    'positions_languages_table',
    db.metadata,
    sqla.Column('positions_id', sqla.Integer, sqla.ForeignKey('positions.id'), primary_key=True),
    sqla.Column('languages_id', sqla.Integer, sqla.ForeignKey('languages.id'), primary_key=True)
)
positions_coursework_table = db.Table(
    'positions_coursework_table',
    db.metadata,
    sqla.Column('positions_id', sqla.Integer, sqla.ForeignKey('positions.id'), primary_key=True),
    sqla.Column('coursework_id', sqla.Integer, sqla.ForeignKey('coursework.id'), primary_key=True)
)
applied_students_table = db.Table(
    "applied_students_table",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id"), primary_key=True),
    db.Column("positions_id", db.Integer, db.ForeignKey("positions.id"), primary_key=True),
)



#------------------ Models ------------------#
class User(db.Model,UserMixin):
    __tablename__='user'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    firstname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120))
    lastname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120))
    password_hash : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(
        sqla.String(256))
    email : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120),
                                                  index = True, unique = True)
    user_type : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))

    #Relationships
    __mapper_args__ = {
        'polymorphic_identity': 'User',
        'polymorphic_on':user_type
        }

    #Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def get_firstname(self):
        return self.firstname

    def get_lastname(self):
        return self.lastname
    
    def get_email(self):
        return self.email

    def get_last_seen_date(self):
        return self.last_seen

class Student(User):
    __tablename__='student'
    id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id),
    primary_key=True)
    username : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64),
    index = True, unique = True)
    gpa: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    last_seen: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))

    #Relationships
    __mapper_args__ = {
        'polymorphic_identity': 'Student'
    }

    majors_of_student = db.relationship(
        'Major',
        secondary=student_majors_table,
        back_populates='students_in_major'
    )
    topics_students = db.relationship(
        'Topic',
        secondary=student_topics_table,
        back_populates='students_topics'
    )
    languages_students = db.relationship(
        'Languages',
        secondary=student_languages_table,
        back_populates='students_languages'
    )
    coursework_students : sqlo.Mapped[list['StudentCoursework']] = sqlo.relationship(
    back_populates='student',
    cascade='all, delete-orphan'
    )
    applied_positions: sqlo.Mapped['Positions'] = sqlo.relationship(
        'Positions',
        secondary=applied_students_table,
        back_populates='applied_students',
    ) 
    applications: sqlo.Mapped["Application"] = sqlo.relationship(back_populates="student", cascade="all, delete")

    #Methods
    def user_applications(self):
        return sqla.select(Application).where(Application.student_id == self.id)
    
    def get_gpa(self):
        return self.gpa
    
    def get_majors(self):
        return self.majors_of_student
    
    def get_topics(self):
        return self.topics_students
    
    def get_languages(self):
        return self.languages_students
    
    def get_coursework(self):
        return self.coursework_students
    

class Faculty(User):
    __tablename__='faculty'
    id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id),
    primary_key=True)
    username : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(64),
    index = True, unique = True)
    verified: sqlo.Mapped[bool] = sqlo.mapped_column(default=False)

    #Relationships
    __mapper_args__ = {
        'polymorphic_identity': 'Faculty'
    }

    positions : sqlo.WriteOnlyMapped['Positions'] = sqlo.relationship(back_populates= 'faculty')
    
    #Methods
    def get_positions(self):
        return db.session.scalars(self.positions.select()).all()
    
    def user_positions(self):
        return sqla.select(Positions).where(Positions.faculty_id == self.id)

class Major(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))

    #Relationships
    students_in_major: sqlo.WriteOnlyMapped['Student'] = sqlo.relationship(
        'Student',
        secondary=student_majors_table,
        back_populates='majors_of_student',
        passive_deletes = True
    )
    positions_in_major: sqlo.WriteOnlyMapped['Positions'] = sqlo.relationship(
        'Positions',
        secondary=positions_majors_table,
        back_populates='majors_positions',
        passive_deletes = True
    )

    #Methods
    def __repr__(self):
        return f"<Major {self.name}>"
    
    def get_major_name(self):
        return self.name

class Topic(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))

    #Relationships
    students_topics: sqlo.WriteOnlyMapped['Student'] = sqlo.relationship(
        'Student',
        secondary=student_topics_table,
        back_populates='topics_students',
        passive_deletes = True
    )
    positions_topics: sqlo.WriteOnlyMapped['Positions'] = sqlo.relationship(
        'Positions',
        secondary=positions_topics_table,
        back_populates='topics_positions',
        passive_deletes = True
    )

    #Methods
    def __repr__(self):
        return f"<Topic {self.name}>"
    
    def get_topic_name(self):
        return self.name

class Languages(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))

    #Relationships
    students_languages: sqlo.WriteOnlyMapped['Student'] = sqlo.relationship(
        'Student',
        secondary=student_languages_table,
        back_populates='languages_students',
        passive_deletes = True
    )
    positions_list: sqlo.WriteOnlyMapped['Positions'] = sqlo.relationship(
        'Positions',
        secondary=positions_languages_table,
        back_populates='languages_positions',
        passive_deletes = True
    )

    #Methods
    def __repr__(self):
        return f"<Languages {self.name}>"
    
    def get_language_name(self):
        return self.name

class Coursework(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    coursenum: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(4), index=True)
    title: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150))
    grade: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(20))
    instructor: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(50))

    #Relationships
    students_coursework: sqlo.Mapped[list['StudentCoursework']] = sqlo.relationship(
    back_populates='coursework',
    cascade='all, delete-orphan'
    )
    positions_coursework: sqlo.WriteOnlyMapped['Positions'] = sqlo.relationship(
        'Positions',
        secondary=positions_coursework_table,
        back_populates='coursework_positions',
        passive_deletes = True
    )

    #Methods
    def __repr__(self):
        return f"<Coursework {self.title}>"

class StudentCoursework(db.Model):
    __tablename__ = 'student_coursework'
    
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(
        sqla.ForeignKey('student.id'), 
        primary_key=True
    )
    coursework_id: sqlo.Mapped[int] = sqlo.mapped_column(
        sqla.ForeignKey('coursework.id'), 
        primary_key=True
    )
    grade: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    
    # Relationships
    student: sqlo.Mapped['Student'] = db.relationship(back_populates='coursework_students')
    coursework: sqlo.Mapped['Coursework'] = db.relationship(back_populates='students_coursework')

#-------------------------------------------------------------------------------------------
class Positions(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    title: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150))
    body: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(2000))
    startdate: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
    enddate: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
    team_size: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
    min_gpa: sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    reference_required: sqlo.Mapped[bool] = sqlo.mapped_column(default=False)
    faculty_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Faculty.id), index = True)

    #Relationships
    # MANY-TO-MANY relationships — use lists like Student
    topics_positions: sqlo.Mapped[list['Topic']] = sqlo.relationship(
        'Topic',
        secondary=positions_topics_table,
        back_populates='positions_topics'
    )
    languages_positions: sqlo.Mapped[list['Languages']] = sqlo.relationship(
        'Languages',
        secondary=positions_languages_table,
        back_populates='positions_list'
    )
    coursework_positions: sqlo.Mapped[list['Coursework']] = sqlo.relationship(
        'Coursework',
        secondary=positions_coursework_table,
        back_populates='positions_coursework'
    )
    majors_positions: sqlo.Mapped[list['Major']] = sqlo.relationship(
        'Major',
        secondary=positions_majors_table,
        back_populates='positions_in_major'
    )
    applied_students: sqlo.Mapped["Student"] = sqlo.relationship(
        secondary=applied_students_table,
        back_populates="applied_positions"
    )
    faculty: sqlo.Mapped["Faculty"] = sqlo.relationship(back_populates="positions")

    student_applications: sqlo.Mapped["Application"] = sqlo.relationship(back_populates="position", cascade="all, delete")

    def approved_count(self):
        return db.session.scalar(
            sqla.select(db.func.count())
            .where(
                Application.position_id == self.id,
                Application.status == "Approved"
            )
    )
    
    def has_space(self):
        return self.approved_count() < self.team_size
    

    

class Application(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    statement: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(2000), nullable=False)
    student_id: sqlo.Mapped[int] = sqlo.mapped_column(
        sqla.ForeignKey("student.id", ondelete="CASCADE"))
    position_id: sqlo.Mapped[int] = sqlo.mapped_column(
        sqla.ForeignKey("positions.id", ondelete="CASCADE"))
    reference_id: sqlo.Mapped[Optional[int]] = sqlo.mapped_column(
        sqla.ForeignKey("faculty.id", ondelete="SET NULL"))
    status: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20), default = "Pending") 
    reference_status: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20), default = "Pending") 
    
    #Relationships
    student: sqlo.Mapped["Student"] = sqlo.relationship(back_populates="applications")
    
    position: sqlo.Mapped["Positions"] = sqlo.relationship(
        back_populates="student_applications")
    
    reference = db.relationship("Faculty")

    #Methods
    def __repr__(self):
        return f"<Application student={self.student_id} position={self.position_id}>"

