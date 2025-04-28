from typing import Optional, List, Dict, Tuple


class TrackHealth:
    """
    Track and analyse basic health metrics: steps, activity duration, heart rate, and blood pressure.
    """

    def __init__(
            self,
            steps: Optional[int] = None,
            steps_goal: int = 10000,
            activity_duration: Optional[int] = None,
            activity_duration_goal: int = 120,
            heart_rate: Optional[List[int]] = None,
            blood_pressure: Optional[Tuple[int, int]] = None,
            age: int = 25
    ) -> None:
        """
        Initialise health tracker with optional user data and goals.
        """
        # Step counts and targets
        self.steps: int = steps or 0
        self.steps_goal: int = steps_goal

        # Activity duration in minutes and target
        self.activity_duration: int = activity_duration or 0
        self.activity_duration_goal: int = activity_duration_goal

        # Heart-rate readings list
        self.heart_rate: List[int] = heart_rate or [50, 64, 153]

        # Optional blood pressure reading (systolic, diastolic)
        self.blood_pressure: Optional[Tuple[int, int]] = blood_pressure

        # User age and lookup table for max heart rate by age bracket
        self.age: int = age
        self.max_heart_age: Dict[int, int] = {
            20: 200, 25: 195,
            30: 190, 35: 185,
            40: 180, 45: 175,
            50: 170, 55: 165,
            60: 160, 65: 155,
            70: 150
        }

    def steps_percentage_complete(self) -> int:
        """
        Compute percentage of daily step goal achieved.
        """
        if not self.steps_goal:
            return 0
        return round((self.steps / self.steps_goal) * 100)

    def activity_percentage_complete(self) -> int:
        """
        Compute percentage of daily activity-duration goal achieved.
        """
        if not self.activity_duration_goal:
            return 0
        return round((self.activity_duration / self.activity_duration_goal) * 100)

    def max_heart_rate(self) -> int:
        """
        Return the highest recorded heart-rate.
        """
        return max(self.heart_rate)

    def min_heart_rate(self) -> int:
        """
        Return the lowest recorded heart-rate.
        """
        return min(self.heart_rate)

    def avg_heart_rate(self) -> int:
        """
        Compute average heart-rate.
        """
        return int(sum(self.heart_rate) / len(self.heart_rate))

    def heart_rate_range(self) -> List[int]:
        """
        Scale min, average and max heart-rate onto a 0–50 bar scale.
        """
        minimum_user = self.min_heart_rate()
        average_user = self.avg_heart_rate()
        maximum_user = self.max_heart_rate()
        base_min, base_max, scale_max = 0, 200, 50
        return [
            round((value - base_min) / (base_max - base_min) * scale_max)
            for value in (minimum_user, average_user, maximum_user)
        ]

    def heart_rate_zones(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate training zones based on age-adjusted max heart-rate,
        naming each zone 'zone_one' through 'zone_five'.
        """
        # Round age to nearest 5-year bracket, capped at 70
        age_key = 5 * round(self.age / 5) if self.age < 70 else 70
        max_hr = self.max_heart_age.get(age_key, 200)

        # Mapping from index to word suffix for zone naming
        map_num: Dict[int, str] = {
            1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'
        }

        zones: Dict[str, Dict[str, int]] = {}
        # Each fraction defines the lower threshold; upper uses fraction + 0.1
        fractions: List[float] = [0.5, 0.6, 0.7, 0.8, 0.9]
        for i, frac in enumerate(fractions, start=1):
            lower = round(max_hr * frac)
            upper = round(max_hr * (frac + 0.1))
            # e.g. 'zone_one', 'zone_two', etc.
            zone_name = f'zone_{map_num[i]}'
            zones[zone_name] = {'minimum': lower, 'maximum': upper}
        return zones

    def heart_rate_zone_progress_bar(self) -> Dict[str, Dict[str, int]]:
        """
        Convert heart-rate zones to a 0–50 scale for progress-bar display.
        """
        zones = self.heart_rate_zones()
        max_hr_possible = 220  # reference for visual scaling
        scale_max = 50
        factor = scale_max / max_hr_possible

        scaled_zones: Dict[str, Dict[str, int]] = {}
        for zone, limits in zones.items():
            scaled_zones[zone] = {
                'min': round(limits['minimum'] * factor),
                'max': round(limits['maximum'] * factor)
            }
        return scaled_zones
