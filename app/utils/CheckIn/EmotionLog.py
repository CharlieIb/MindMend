from app.models import EmotionLog
from typing import List, Optional
from datetime import datetime
import sqlalchemy as sa


class EmotionLogManager:
    EMOTIONS = [
        {"title": "Anxious", "feelings": ["Nervous", "Overwhelmed", "Irritable", "Restless", "Worried"],
         "button-color": "btn btn-outline-secondary"},
        {"title": "Calm", "feelings": ["Relaxed", "Peaceful", "Content", "At Ease", "Serene"],
         "button-color": "btn btn-outline-primary"},
        {"title": "Happy", "feelings": ["Joyful", "Excited", "Optimistic", "Grateful", "Energetic"],
         "button-color": "btn btn-outline-warning"},
        {"title": "Sad", "feelings": ["Down", "Lonely", "Disheartened", "Hopeless", "Heartbroken"],
         "button-color": "btn btn-outline-info"},
        {"title": "Anger", "feelings": ["Irritated", "Vexed", "Raged", "Annoyed", "Cross"],
         "button-color": "btn btn-outline-danger"},
        {"title": "Love", "feelings": ["Affectionate", "Empathetic", "Grateful", "Warm", "Loved"],
         "button-color": "btn btn-outline-success"}
    ]

    FEELING_TO_PARENT = {
        feeling: info['title']
        for info in EMOTIONS
        for feeling in info['feelings']
    }

    @classmethod
    def list_emotions(cls):
        """Lists all emotions and information associated with them.

        Returns:
            EMOTIONS
        """
        return cls.EMOTIONS

    def __init__(self, session, user_id):
        self.session = session
        self.user_id = user_id
        self.emotional_logs = self._load_emotional_logs_by_user(self.user_id)

    def _load_emotional_logs_by_user(self, user_id):
        """Load the emotion logs for a user"""
        q = sa.select(EmotionLog).where(EmotionLog.user_id == user_id)
        return {log.log_id: log for log in self.session.execute(q).scalars().all()}

    def get_emotion_log(self, log_id):
        """Get an emotional log by its ID"""
        return self.emotional_logs.get(log_id)

    def add_new_log(
            self,
            emotion: str,
            steps: int,
            activity_duration: Optional[int] = None,
            heart_rate: Optional[int] = None,
            blood_pressure: Optional[int] = None,
            free_notes: Optional[str] = None,
            location_id: Optional[int] = None,
            activity_id: Optional[int] = None,
            person_id: Optional[int] = None
    ):
        """
        Add new emotional log to the database and in-memory storage
        """
        new_log = EmotionLog(
            user_id=self.user_id,
            time=datetime.now(),
            emotion=self.map_emotions_to_parent(emotion),
            steps=steps,
            activity_duration=activity_duration,
            heart_rate=heart_rate,
            blood_pressure=blood_pressure,
            free_notes=free_notes,
            location_id=location_id,
            activity_id=activity_id,
            person_id=person_id
        )
        self.session.add(new_log)
        self.session.commit()

    def delete_log(self, log_id):
        """Delete a log by its ID"""
        log = self.get_emotion_log(log_id)
        if not log:
            return False

        self.session.delete(log)
        self.session.commit()

        del self.emotional_logs[log_id]
        return True

    def map_emotions_to_parent(self, emotion):
        """
        Maps emotions to their parent emotion.

        Returns:
            Parent Emotion.
        """
        return self.FEELING_TO_PARENT.get(emotion)
