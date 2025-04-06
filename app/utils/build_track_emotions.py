class TrackEmotions:
    def __init__(self, data_log=None):
        self.data_log = data_log or self._fake_data_log_raw()

    def count_emotions(self):
        logs_mapping = self._create_logs_mapping(self.data_log)
        counts = {}
        for title, details in logs_mapping.items():
            current_length = len(details['logs'])
            counts[title.lower()] = {'length': current_length, 'colour': details['colour']}
        return counts

    @staticmethod
    def _fake_data_log_raw():
        return [
            "Grateful", "Disheartened", "Grateful", "Down", "Optimistic",
            "Irritable", "Worried", "Excited", "Heartbroken", "Restless",
            "Overwhelmed", "Nervous", "Grateful", "Lonely", "Excited",
            "Disheartened", "Optimistic", "Energetic", "Lonely", "Hopeless",
            "Relaxed", "Relaxed", "Content", "Grateful", "Joyful", "Excited"
        ]

    @staticmethod
    def _create_logs_mapping(logs: list) -> dict:
        emotions_map = [
            {
                "title": "Anxious",
                "feelings": ["Nervous", "Overwhelmed", "Irritable", "Restless", "Worried"],
                "colour": "danger"
            },
            {
                "title": "Calm",
                "feelings": ["Relaxed", "Peaceful", "Content", "At Ease", "Serene"],
                "colour": "info"
            },
            {
                "title": "Happy",
                "feelings": ["Joyful", "Excited", "Optimistic", "Grateful", "Energetic"],
                "colour": "warning"
            },
            {
                "title": "Sad",
                "feelings": ["Down", "Lonely", "Disheartened", "Hopeless", "Heartbroken"],
                "colour": "success"
            }
        ]

        logs_mapping = {
            emotion['title']: {
                "colour": emotion['colour'],
                "logs": [log for log in logs if log in emotion['feelings']]
            }
            for emotion in emotions_map
        }
        return logs_mapping
