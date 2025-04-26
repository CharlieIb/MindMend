import sqlalchemy as sa
from datetime import datetime, timedelta
from collections import Counter
from flask_login import current_user
from typing import Optional, List, Dict, Any, cast
from app.models import Notification, EmotionLog


class NotificationService:
    """
    Service to manage creation and retrieval of user notifications.
    """

    def __init__(self, db_session, user=None):
        self.db = db_session
        # Default to the current logged-in user if none provided
        self.user = user or current_user

    @staticmethod
    def should_notify(latest_time: datetime, period_days: int = 1) -> bool:
        return (datetime.utcnow() - latest_time) >= timedelta(days=period_days)

    def create_notification(self, message: str, frequency: str, link: str) -> Notification:
        notif = Notification(
            user_id=self.user.id,
            time=datetime.utcnow(),
            message=message,
            frequency=frequency,
            link=link
        )
        self.db.add(notif)
        self.db.commit()
        return notif

    def get_last_notification_time(self, frequency: str) -> Optional[datetime]:
        """
        Returns the timestamp of the most recent notification for the given frequency,
        or None if no notification exists.
        """
        stmt = (
            sa.select(Notification.time)
            .where(
                Notification.user_id == self.user.id,
                Notification.frequency == frequency
            )
            .order_by(Notification.time.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def get_last_notifications(self, limit: int) -> List[Notification]:
        stmt = (
            sa.select(Notification)
            .where(Notification.user_id == self.user.id)
            .order_by(Notification.time.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def daily_notification(self, logs: List[EmotionLog]) -> Optional[Notification]:
        last_daily = self.get_last_notification_time('daily')
        if last_daily and last_daily.date() == datetime.utcnow().date():
            return None

        latest_log_time = cast(datetime, logs[-1].time) if logs else None
        should_alert = (latest_log_time is None or
                        self.should_notify(latest_log_time, period_days=1))

        if should_alert:
            return self.create_notification(
                "Don't forget to do your Check-In logs today!",
                'daily',
                'emotion_log'
            )
        return None

    def weekly_notification(self, logs: List[EmotionLog]) -> Optional[Notification]:
        last_weekly = self.get_last_notification_time('weekly')
        if last_weekly and not self.should_notify(last_weekly, period_days=7):
            return None

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        recent = [log for log in logs if week_ago <= cast(datetime, log.time) <= now]

        if not recent:
            msg = (
                "You haven't logged any emotions last week. "
                "Go to Check-In to get started."
            )
        else:
            counts = Counter(log.emotion for log in recent)
            top, cnt = counts.most_common(1)[0]
            msg = (
                f"You logged feeling {top} the most in the last week:"
                f"\n{cnt} out of {len(recent)} entries."
            )

        return self.create_notification(msg, 'weekly', link='emotion_log')

    def get_notifications(self, limit: int = 15) -> Dict[str, Any]:
        """
        Creates daily/weekly notifications if needed and returns the latest notifications.
        """
        # Fetch emotion logs ordered chronologically
        stmt = (
            sa.select(EmotionLog)
            .where(EmotionLog.user_id == self.user.id)
            .order_by(EmotionLog.time)
        )
        logs = self.db.scalars(stmt).all()
        all_logs = len(logs)

        # Possibly create daily & weekly notifications
        self.daily_notification(logs)
        self.weekly_notification(logs)

        # Retrieve the latest notifications
        last_notifications = self.get_last_notifications(limit)

        all_read = all(notif.is_read for notif in last_notifications)
        return {
            'all_read': all_read,
            'notifications': last_notifications,
            'all_logs': all_logs
        }
