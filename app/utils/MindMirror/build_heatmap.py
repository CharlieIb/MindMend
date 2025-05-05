import calendar
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple


class HeatMap:
    """
    Create and manage a heatmap display from logged emotions.
    """

    def __init__(
            self,
            dd: Optional[int] = None,
            mm: Optional[int] = None,
            yy: Optional[int] = None,
            data_log: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Initialise HeatMap with an optional date and log data.

        Args:
            dd: Day of month; defaults to current day.
            mm: Month number; defaults to current month.
            yy: Year number; defaults to current year.
            data_log: List of logs, each a dict with keys 'date', 'emotion', and 'colour'.
        """
        now = datetime.now()
        self.dd = dd or now.day
        self.mm = mm or now.month
        self.yy = yy or now.year
        self.data_log = data_log or []

    def month_display(self) -> List[List[int] | List[List[int]]]:
        """
        Generate layout for a single month's heatmap.

        Returns:
            A two-element list:
            - [month, year]
            - Calendar layout as a list of weeks, each week a list of day values
              where days with log data are replaced by [day, log_data].
        """
        month_info = [[self.mm, self.yy], calendar.monthcalendar(self.yy, self.mm)]
        logs_mapping = self._create_logs_mapping(self.group_emotions() or self.data_log)
        for week in month_info[1]:
            for idx, day in enumerate(week):
                if day != 0 and (day, self.mm, self.yy) in logs_mapping:
                    week[idx] = [day, logs_mapping[(day, self.mm, self.yy)]]
        return month_info

    def year_display(self) -> List[List[int] | List[List[int]]]:
        """
        Generate layout for an entire year's heatmap.

        Returns:
            A list of 12 elements (one per month), each a two-element list:
            - [month, year]
            - Calendar layout as a list of weeks, with days possibly replaced by [day, log_data].
        """
        logs_mapping = self._create_logs_mapping(self.group_emotions() or self.data_log)
        year_layout: List[List[int] | List[List[int]]] = []
        for month in range(1, 13):
            month_cal = calendar.monthcalendar(self.yy, month)
            for week in month_cal:
                for idx, day in enumerate(week):
                    if day != 0 and (day, month, self.yy) in logs_mapping:
                        week[idx] = [day, logs_mapping[(day, month, self.yy)]]
            year_layout.append([[month, self.yy], month_cal])
        return year_layout

    def group_emotions(self) -> List[Dict[str, str]]:
        """
        Map each log entry to its display colour.

        Returns:
            A list of dicts with keys:
            - 'date': date from log.
            - 'emotion': emotion label.
            - 'colour': associated colour name.
        """
        emotions_table = [
            {'emotion': 'Anger', 'colour': 'red'},
            {'emotion': 'Anxious', 'colour': 'grey'},
            {'emotion': 'Sad', 'colour': 'blue'},
            {'emotion': 'Happy', 'colour': 'yellow'},
            {'emotion': 'Love', 'colour': 'green'},
            {'emotion': 'Calm', 'colour': 'dark_blue'}
        ]
        mapped: List[Dict[str, str]] = []
        for log in self.data_log:
            entry = {'date': log['date'], 'emotion': log['emotion']}
            for info in emotions_table:
                if log['emotion'] == info['emotion']:
                    entry['colour'] = info['colour']
                    break
            if 'colour' in entry:
                mapped.append(entry)
        return mapped

    @staticmethod
    def _create_logs_mapping(
            logs: List[Dict[str, Any]]
    ) -> Dict[Tuple[int, int, int], Dict[str, str]]:
        """
        Build a lookup mapping dates to emotion data for past logs.

        Args:
            logs: List of logs, each with 'date', 'emotion', and 'colour'.

        Returns:
            A dict mapping (day, month, year) to {'emotion': ..., 'colour': ...},
            including only logs with date <= now().
        """
        now = datetime.now()
        return {
            (log['date'].day, log['date'].month, log['date'].year): {
                'emotion': log['emotion'],
                'colour': log['colour']
            }
            for log in logs
            if log['date'] <= now
        }
