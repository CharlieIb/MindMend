from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime

Base = so.declarative_base()


# User table
class User(UserMixin, db.Model, Base):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(24), nullable=False, default='Normal')

    # Relationships:
    emotion_logs: so.Mapped[list['EmotionLog']] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    test_result: so.Mapped[list['TestResult']] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: so.Mapped[list['Notification']] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    support_request: so.Mapped['SupportRequest'] = so.relationship(back_populates="user", cascade="all, delete-orphan")


    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, role={self.role})"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


## CheckIn Tables
# People Table - could be removed
class Person(db.Model):
    __tablename__ = "person"

    person_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped['EmotionLog'] = so.relationship(back_populates="person")



# Location Table - could be removed
class Location(db.Model):
    __tablename__ = "locations"

    location_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped['EmotionLog'] = so.relationship(back_populates="location")



# Activity Table - could be removed
class Activity(db.Model):
    __tablename__ = "activities"

    activity_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped['EmotionLog'] = so.relationship(back_populates="activity")



# EmotionLog Table
class EmotionLog(db.Model):
    __tablename__ = "emotion_logs"

    log_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    emotion: so.Mapped[str] = so.mapped_column(sa.String(50))
    steps: so.Mapped[int] = so.mapped_column(sa.Integer) # Maybe update this to be nullable
    activity_duration: so.Mapped[int] = so.mapped_column(nullable=True)
    heart_rate: so.Mapped[int] = so.mapped_column(nullable=True)
    blood_pressure: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)
    free_notes: so.Mapped[sa.Text] = so.mapped_column(sa.Text, nullable=True)

    # Foreign Keys
    location_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey("location.location_id"), nullable=True)
    activity_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey("activity.activity_id"), nullable=True)
    person_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey("person.person_id"), nullable=True)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="emotion_logs")
    location: so.Mapped['Location'] = so.relationship(back_populates="emotion_logs")
    activity: so.Mapped['Activity'] = so.relationship(back_populates="emotion_logs")
    people: so.Mapped['Person'] = so.relationship(back_populates="emotion_logs")

    # user = so.relationship("User", backref="emotion_logs")
    # location = so.relationship("Location", backref="emotion_logs")
    # activity = so.relationship("Activity", backref="emotion_logs")
    # people = so.relationship("Person", backref="emotion_logs")


##Screening Tool tables
# Condition Table
class Condition(db.Model):
    __tablename__ = "conditions"

    cond_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False, unique=True)
    threshold: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)


    # Relationships:
    questions: so.Mapped[list['ConditionQuestion']] = so.relationship(back_populates="condition", cascade="all, delete-orphan")
    test_result: so.Mapped[list['TestResult']] = so.relationship(back_populates="condition", cascade="all, delete-orphan")


    # Relationships through secondary tables
    therapeutic_recs: so.Mapped[list['TherapeuticRec']] = so.relationship(
        secondary="therapeutic_rec_condition",
        back_populates="conditions"
    )
    resources: so.Mapped[list['Resource']] = so.relationship(
        secondary="resource_condition",
        back_populates="conditions"
    )


# Condition Questionnaire Questions
class ConditionQuestion(db.Model):
    __tablename__ = "condition_questions"

    cond_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("condition.cond_id"), primary_key=True)
    q_number: so.Mapped[int] = so.mapped_column(primary_key=True)
    question: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    value: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)

    # Relationships
    condition: so.Mapped['Condition'] = so.relationship(back_populates="questions")

    # condition = so.relationship("Condition", backref="questions")


# Test Result Table
class TestResult(db.Model):
    __tablename__ = "test_results"

    test_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    cond_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("condition.cond_id"), nullable=False)
    result: so.Mapped[str] = so.mapped_column(sa.Text)
    timedate: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="test_result")
    condition: so.Mapped['Condition'] = so.relationship(back_populates="test_result")


    #user = so.relationship("User", backref="test_results")
    #condition = so.relationship("Condition", backref="test_results")


# Therapeutic Recommendations Table
class TherapeuticRec(db.Model):
    __tablename__ = "therapeutic_recs"

    rec_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False, unique=True)
    evidence_based: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    source: so.Mapped[str] = so.mapped_column(sa.String(256))
    treatments: so.Mapped[str] = so.mapped_column(sa.Text)

    # Relationship:
    conditions: so.Mapped[list['Condition']] = so.relationship(
        secondary="therapeutic_rec_condition",
        back_populates="conditions"
    )


# Resource Table
class Resource(db.Model):
    __tablename__ = "resources"

    resource_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    label: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False, unique=True)
    link: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)

    # Relationship:
    conditions: so.Mapped[list['Condition']] = so.relationship(
        secondary="resource_condition",
        back_populates="conditions"
    )


# Associate table: Therapeutic Rec and Condition
therapeutic_rec_condition = sa.Table(
    "therapeutic_rec_conditions",
    db.metadata,
    sa.Column("therapeutic_id", sa.ForeignKey("therapeutic_rec.rec_id"), primary_key=True),
    sa.Column("condition_id", sa.ForeignKey("condition.cond_id"), primary_key=True)
)

# Association table: Resource and Condition
resource_condition = sa.Table(
    "resource_conditions",
    db.metadata,
    sa.Column("resource_id", sa.ForeignKey("resource.resource_id"), primary_key=True),
    sa.Column("condition_id", sa.ForeignKey("condition.cond_id"), primary_key=True)
)


## Mind Mirror
# Notifications
class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    message: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    is_read: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="notifications")


## ReachOut
# SupportRequest
class SupportRequest(db.Model):
    __tablename__ = "support_requests"

    request_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="support_request")
