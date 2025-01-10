import calendar
from datetime import date, timedelta

class Calendar:
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def get_month_days(self):
        cal = calendar.Calendar()
        return cal.monthdayscalendar(self.year, self.month)

class WeekCalendar:
    def __init__(self, start_date):
        self.start_date = start_date

    def get_week_days(self):
        """Returns a list of dates for the week starting from `start_date`."""
        return [self.start_date + timedelta(days=i) for i in range(7)]