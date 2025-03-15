import calendar
from datetime import datetime


class HeatMap:
    def __init__(self, dd=None, mm=None, yy=None):
        now = datetime.now()
        self.dd = dd or now.day
        self.mm = mm or now.month
        self.yy = yy or now.year
        self.current_day = now.date()

    def month_display(self):
        month_info = [[self.mm, self.yy], calendar.monthcalendar(self.yy, self.mm)]
        logs_mapping = self._create_logs_mapping(self.fake_data_log_raw())
        for week in month_info[1]:
            for i, day in enumerate(week):
                if day != 0 and (day, self.mm, self.yy) in logs_mapping:
                    week[i] = [week[i], logs_mapping[day, self.mm, self.yy]]
        return month_info

    def year_display(self):
        logs_mapping = self._create_logs_mapping(self.fake_data_log_raw())
        days_in_year = []
        # for m in range(1, 13):
        #     days_in_year.append([[m, self.yy], calendar.monthcalendar(self.yy, m)])
        for m in range(1, 13):
            month_cal = calendar.monthcalendar(self.yy, m)
            for week in month_cal:
                for i, day in enumerate(week):
                    if day != 0 and (day, m, self.yy) in logs_mapping:
                        week[i] = [week[i], logs_mapping[(day, m, self.yy)]]
            days_in_year.append([[m, self.yy], month_cal])
        return days_in_year

    @staticmethod
    def fake_data_log_raw():
        return [
            {'date': datetime.strptime('02/01/2025', '%d/%m/%Y'), 'emotion': 'Anxious', 'colour': 'danger'},
            {'date': datetime.strptime('09/01/2025', '%d/%m/%Y'), 'emotion': 'Calm', 'colour': 'info'},
            {'date': datetime.strptime('11/01/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('15/01/2025', '%d/%m/%Y'), 'emotion': 'Sad', 'colour': 'success'},
            {'date': datetime.strptime('17/01/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('22/01/2025', '%d/%m/%Y'), 'emotion': 'Calm', 'colour': 'info'},
            {'date': datetime.strptime('28/01/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('30/01/2025', '%d/%m/%Y'), 'emotion': 'Anxious', 'colour': 'danger'},
            {'date': datetime.strptime('04/02/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('08/02/2025', '%d/%m/%Y'), 'emotion': 'Anxious', 'colour': 'danger'},
            {'date': datetime.strptime('10/02/2025', '%d/%m/%Y'), 'emotion': 'Sad', 'colour': 'success'},
            {'date': datetime.strptime('14/02/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('19/02/2025', '%d/%m/%Y'), 'emotion': 'Anxious', 'colour': 'danger'},
            {'date': datetime.strptime('23/02/2025', '%d/%m/%Y'), 'emotion': 'Calm', 'colour': 'info'},
            {'date': datetime.strptime('26/02/2025', '%d/%m/%Y'), 'emotion': 'Anxious', 'colour': 'danger'},
            {'date': datetime.strptime('01/03/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('02/03/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('04/03/2025', '%d/%m/%Y'), 'emotion': 'Happy', 'colour': 'warning'},
            {'date': datetime.strptime('05/03/2025', '%d/%m/%Y'), 'emotion': 'Calm', 'colour': 'info'},
            {'date': datetime.strptime('08/03/2025', '%d/%m/%Y'), 'emotion': 'Sad', 'colour': 'success'},
            {'date': datetime.strptime('09/03/2025', '%d/%m/%Y'), 'emotion': 'Sad', 'colour': 'success'},
            {'date': datetime.strptime('13/03/2025', '%d/%m/%Y'), 'emotion': 'Calm', 'colour': 'info'},
            {'date': datetime.strptime('15/03/2025', '%d/%m/%Y'), 'emotion': 'Sad', 'colour': 'success'}
        ]

    @staticmethod
    def _create_logs_mapping(logs: list) -> dict:
        return {
            (log['date'].day, log['date'].month, log['date'].year):
                {'emotion': log['emotion'], 'colour': log['colour']}
            for log in logs
        }

print(HeatMap().year_display())