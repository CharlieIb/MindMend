import calendar
from datetime import datetime


class HeatMap:
    def __init__(self, dd=None, mm=None, yy=None, data_log=None):
        now = datetime.now()
        self.dd = dd or now.day
        self.mm = mm or now.month
        self.yy = yy or now.year
        self.data_log = data_log

    def month_display(self):
        month_info = [[self.mm, self.yy], calendar.monthcalendar(self.yy, self.mm)]
        logs_mapping = self._create_logs_mapping(self.group_emotions() or self.data_log)
        for week in month_info[1]:
            for i, day in enumerate(week):
                if day != 0 and (day, self.mm, self.yy) in logs_mapping:
                    week[i] = [week[i], logs_mapping[day, self.mm, self.yy]]
        return month_info

    def year_display(self):
        logs_mapping = self._create_logs_mapping(self.group_emotions() or self.data_log)
        days_in_year = []
        for m in range(1, 13):
            month_cal = calendar.monthcalendar(self.yy, m)
            for week in month_cal:
                for i, day in enumerate(week):
                    if day != 0 and (day, m, self.yy) in logs_mapping:
                        week[i] = [week[i], logs_mapping[(day, m, self.yy)]]
            days_in_year.append([[m, self.yy], month_cal])
        return days_in_year

    def group_emotions(self):
        emotions_table = [
            {'emotion': 'Anger', 'colour': 'dark_red'},
            {'emotion': 'Anxious', 'colour': 'red'},
            {'emotion': 'Sad', 'colour': 'dark_blue'},
            {'emotion': 'Happy', 'colour': 'bright_yellow'},
            {'emotion': 'Love', 'colour': 'hot_pink'},
            {'emotion': 'Calm', 'colour': 'light_blue'}
        ]

        group_data = []
        for log in self.data_log:
            data = {'date': log['date'], 'emotion': log['emotion']}
            for info in emotions_table:
                if log['emotion'] == info['emotion']:
                    data['colour'] = info['colour']
                    break
            if len(data) == 3:
                group_data.append(data)

        return group_data

    @staticmethod
    def _create_logs_mapping(logs: list) -> dict:
        return {
            (log['date'].day, log['date'].month, log['date'].year):
                {'emotion': log['emotion'], 'colour': log['colour']}
            for log in logs if log['date'] <= datetime.now()
        }
