import calendar
from datetime import datetime


class HeatMap:
    def __init__(self, dd, mm, yy):
        self.dd = dd if dd else datetime.now().day
        self.mm = mm
        self.yy = yy

    def month_display(self):
        month = calendar.monthcalendar(self.yy, self.mm)
        return month


HeatMap(13, 3, 2025).month_display()
