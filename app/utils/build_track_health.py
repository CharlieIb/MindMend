class TrackHealth:
    def __init__(self,
                 steps=None,
                 steps_goal=10000,
                 activity_duration=None,
                 activity_duration_goal=2,
                 heart_rate=None,
                 blood_pressure=None
                 ):
        self.steps = steps
        self.steps_goal = steps_goal
        self.activity_duration = activity_duration
        self.activity_duration_goal = activity_duration_goal
        self.heart_rate = heart_rate
        self.blood_pressure = blood_pressure

    def steps_percentage_complete(self):
        return (self.steps / self.steps_goal) * 100

    def max_heart_rate(self):
        return max(self.heart_rate)

    def min_heart_rate(self):
        return min(self.heart_rate)