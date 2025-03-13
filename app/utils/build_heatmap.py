import calendar


class HeatMap:
    def __init__(self, dd, mm, yy):
        self.dd = dd
        self.mm = mm
        self.yy = yy

    def month_display(self):
        month = calendar.monthcalendar(self.yy, self.mm)
        return month

    def year_display(self):
        year = []
        for m in range(1, 13):
            year.append(calendar.monthcalendar(self.yy, m))
        return year
