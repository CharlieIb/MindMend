from typing import Optional, Dict, Any
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime


# User table
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(24), nullable=False, default='Normal')
    track_physiological: so.Mapped[bool] = so.mapped_column(default=False, nullable=False)
    share_data: so.Mapped[bool] = so.mapped_column(default=False, nullable=False)

    # Relationships
    user_settings: so.Mapped['UserSettings'] = so.relationship(back_populates="user", cascade="all, delete-orphan",
                                                               uselist=False)
    emotion_logs: so.Mapped[list['EmotionLog']] = so.relationship(back_populates="user")
    test_result: so.Mapped[list['TestResult']] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: so.Mapped[list['Notification']] = so.relationship(back_populates="user",
                                                                     cascade="all, delete-orphan")
    support_request: so.Mapped['SupportRequest'] = so.relationship(back_populates="user", cascade="all, delete-orphan",
                                                                    uselist=False)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, role={self.role}, track_physiological={self.track_physiological})"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    # Need app context for db.session
    with current_app.app_context():
        # Eager loading for emotion logs and user_settings to ensure they are loaded when the user logs in
        return db.session.execute(
            db.select(User).filter_by(id=int(id)).options(
                so.joinedload(User.emotion_logs),
                so.joinedload(User.user_settings)
            )
        ).unique().scalar_one_or_none()


## User Settings
class UserSettings(db.Model):
    __tablename__ = 'users_settings'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    mind_mirror_display: so.Mapped[Dict[str, Any]] = so.mapped_column(
        sa.JSON, default=lambda: {
            'heatmap': True,
            'emotion_graph': True,
            'emotion_info': True,
            'track_activity': True,
            'track_steps': True,
            'track_heart_rate': True,
            'heart_zones': True
        }, nullable=False
    )

    # Relationship
    user: so.Mapped['User'] = so.relationship(back_populates="user_settings")


@sa.event.listens_for(User, 'after_insert')
def create_user_settings(mapper, connection, target):
    stmt = UserSettings.__table__.insert().values(
        user_id=target.id,
        mind_mirror_display={
            'heatmap': True,
            'emotion_graph': True,
            'emotion_info': True,
            'track_activity': False,
            'track_steps': False,
            'track_heart_rate': False,
            'heart_zones': False
        }
    )
    connection.execute(stmt)


## CheckIn Tables
# People Table
class Person(db.Model):
    __tablename__ = "people"

    person_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped[list['EmotionLog']] = so.relationship(back_populates="person")


# Location Table
class Location(db.Model):
    __tablename__ = "locations"

    location_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped[list['EmotionLog']] = so.relationship(back_populates="location")


# Activity Table
class Activity(db.Model):
    __tablename__ = "activities"

    activity_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)

    # Relationships:
    emotion_logs: so.Mapped[list['EmotionLog']] = so.relationship(back_populates="activity")


# EmotionLog Table
class EmotionLog(db.Model):
    __tablename__ = "emotion_logs"

    log_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    emotion: so.Mapped[str] = so.mapped_column(sa.String(50))
    steps: so.Mapped[int] = so.mapped_column(sa.Integer)
    activity_duration: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    heart_rate: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    blood_pressure: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), nullable=True)
    free_notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)

    # Foreign Keys
    location_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey("locations.location_id"),
                                                             nullable=True)
    activity_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey("activities.activity_id"),
                                                             nullable=True)
    person_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey("people.person_id"), nullable=True)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="emotion_logs")
    location: so.Mapped[Optional['Location']] = so.relationship(back_populates="emotion_logs")
    activity: so.Mapped[Optional['Activity']] = so.relationship(back_populates="emotion_logs")
    person: so.Mapped[Optional['Person']] = so.relationship(back_populates="emotion_logs")

    def __repr__(self):
        return (f"EmotionLog("
                f"Log Id: {self.log_id}, User Id: {self.user_id}, Time: {self.time}, "
                f"Emotion: {self.emotion}, Steps: {self.steps}, Activity Duration: {self.activity_duration}, "
                f"Heart_rate: {self.heart_rate}, Blood Pressure: {self.blood_pressure}, "
                f"Free Notes: {self.free_notes})")


##Screening Tool tables
# Condition Table
class Condition(db.Model):
    __tablename__ = "conditions"

    cond_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False, unique=True)
    threshold: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)

    # Relationships:
    questions: so.Mapped[list['ConditionQuestion']] = so.relationship(back_populates="condition",
                                                                      cascade="all, delete-orphan")
    test_result: so.Mapped[list['TestResult']] = so.relationship(back_populates="condition",
                                                                 cascade="all, delete-orphan")

    # Relationships through secondary tables
    therapeutic_recs: so.Mapped[list['TherapeuticRec']] = so.relationship(
        secondary="therapeutic_rec_conditions",
        back_populates="conditions"
    )
    resources: so.Mapped[list['Resource']] = so.relationship(
        secondary="resource_conditions",
        back_populates="conditions"
    )


# Condition Questionnaire Questions
class ConditionQuestion(db.Model):
    __tablename__ = "condition_questions"

    cond_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("conditions.cond_id"), primary_key=True)
    q_number: so.Mapped[int] = so.mapped_column(primary_key=True)
    question: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    value: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)

    # Relationships
    condition: so.Mapped['Condition'] = so.relationship(back_populates="questions")


# Test Result Table
class TestResult(db.Model):
    __tablename__ = "test_results"

    test_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    cond_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("conditions.cond_id"), nullable=False)
    result: so.Mapped[str] = so.mapped_column(sa.Text)
    timedate: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="test_result")
    condition: so.Mapped['Condition'] = so.relationship(back_populates="test_result")


# Therapeutic Recommendations Table
class TherapeuticRec(db.Model):
    __tablename__ = "therapeutic_recs"

    rec_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False, unique=True)
    treatments: so.Mapped[str] = so.mapped_column(sa.Text)

    # Relationship:
    conditions: so.Mapped[list['Condition']] = so.relationship(
        secondary="therapeutic_rec_conditions",
        back_populates="therapeutic_recs"
    )


# Resource Table
class Resource(db.Model):
    __tablename__ = "resources"

    resource_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    label: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False, unique=True)
    link: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)

    # Relationship:
    conditions: so.Mapped[list['Condition']] = so.relationship(
        secondary="resource_conditions",
        back_populates="resources"
    )


# Associate table: Therapeutic Rec and Condition
therapeutic_rec_condition = sa.Table(
    "therapeutic_rec_conditions",
    db.metadata,
    sa.Column("therapeutic_id", sa.ForeignKey("therapeutic_recs.rec_id"), primary_key=True),
    sa.Column("condition_id", sa.ForeignKey("conditions.cond_id"), primary_key=True)
)

# Association table: Resource and Condition
resource_condition = sa.Table(
    "resource_conditions",
    db.metadata,
    sa.Column("resource_id", sa.ForeignKey("resources.resource_id"), primary_key=True),
    sa.Column("condition_id", sa.ForeignKey("conditions.cond_id"), primary_key=True)
)


## Mind Mirror
# Notifications
class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    message: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    is_read: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    frequency: so.Mapped[str] = so.mapped_column(sa.String(24), nullable=True)
    link: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="notifications")


## ReachOut
# SupportRequest
class SupportRequest(db.Model):
    __tablename__ = "support_requests"

    request_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False, unique=True)
    time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates="support_request")
