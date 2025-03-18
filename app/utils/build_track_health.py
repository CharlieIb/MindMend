class TrackHealth:
    def __init__(self,
                 steps=None,
                 steps_goal=10000,
                 activity_duration=None,
                 activity_duration_goal=120,
                 heart_rate=None,
                 blood_pressure=None,
                 age=800
                 ):
        self.steps = steps
        self.steps_goal = steps_goal
        self.activity_duration = activity_duration
        self.activity_duration_goal = activity_duration_goal
        self.heart_rate = heart_rate or [50, 64, 153]
        self.blood_pressure = blood_pressure
        self.age = age
        self.max_heart_age = {
            20: 200, 25: 195,
            30: 190, 35: 185,
            40: 180, 45: 175,
            50: 170, 55: 165,
            60: 160, 65: 155,
            70: 150
        }

    def steps_percentage_complete(self):
        return round((self.steps / self.steps_goal) * 100)

    def activity_percentage_complete(self):
        return round((self.activity_duration / self.activity_duration_goal) * 100)

    def max_heart_rate(self):
        return max(self.heart_rate)

    def min_heart_rate(self):
        return min(self.heart_rate)

    def avg_heart_rate(self):
        return int(sum(self.heart_rate) / len(self.heart_rate))

    def heart_rate_range(self):
        minimum_user = self.min_heart_rate()
        average_user = self.avg_heart_rate()
        maximum_user = self.max_heart_rate()
        minimum, maximum = 0, 200

        heart_info = [minimum_user, average_user, maximum_user]
        for i in range(len(heart_info)):
            heart_info[i] = round((heart_info[i] - minimum) / (maximum - minimum) * (50 - minimum) + minimum)
        return heart_info

    def heart_rate_zones(self):
        age = 5 * round(self.age / 5) if self.age < 70 else 70
        max_heart_rate = self.max_heart_age[age]

        zone_one = {'minimum': max_heart_rate * 0.5, 'maximum': max_heart_rate * 0.6}
        zone_two = {'minimum': max_heart_rate * 0.6, 'maximum': max_heart_rate * 0.7}
        zone_three = {'minimum': max_heart_rate * 0.7, 'maximum': max_heart_rate * 0.8}
        zone_four = {'minimum': max_heart_rate * 0.8, 'maximum': max_heart_rate * 0.9}
        zone_five = {'minimum': max_heart_rate * 0.9, 'maximum': max_heart_rate * 1}

        zones = {
            'zone_one': zone_one,
            'zone_two': zone_two,
            'zone_three': zone_three,
            'zone_four': zone_four,
            'zone_five': zone_five
        }
        return zones

    def heart_rate_zone_progress_bar(self):
        zones = self.heart_rate_zones()

        max_heart_rate = 220
        scale = 50
        factor = scale / max_heart_rate

        scaled_zones = {}
        for zone, limits in zones.items():
            scaled_min = limits['minimum'] * factor
            scaled_max = limits['maximum'] * factor
            scaled_zones[zone] = {'min': scaled_min, 'max': scaled_max}

        return scaled_zones

TrackHealth().heart_rate_range()