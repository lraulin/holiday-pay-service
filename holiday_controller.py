import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO, StringIO

HOLIDAY_MULTIPLIER = 0.5

# Column Headers
CREATED_AT = 'Created At (UTC)'
HOURS_WORKED = 'Hours Worked'
HOLIDAY_HOURS = 'X-Holiday Hours'
HOLIDAY_PAY = 'X-Holiday Pay'
LUNCH = 'Lunch (in mins)'
NONHOLIDAY_HOURS = 'X-Non-holiday Hours'
NONHOLIDAY_PAY = 'X-Non-Holiday Pay'
OVERTIME_HOURS_WORKED = 'Overtime Hours Worked'
OVERTIME_PAY_RATE = 'Overtime Pay Rate'
PAY_RATE = 'Pay Rate'
REGULAR_HOURS_WORKED = 'Regular Hours Worked'
TOTAL_PAY = 'X-Total Pay'
START_TIME = 'Start Time'
END_TIME = 'End Time'
NAME = 'Name'


def delta_to_hours(delta: timedelta):
    seconds_in_hour = 3600
    return delta.seconds / seconds_in_hour


def calc_holiday_hours(holiday: datetime, row) -> float:
    holiday_end = holiday + timedelta(days=1)
    start_time = datetime.strptime(row['Start Time'], '%Y-%m-%d %I:%M %p')
    end_time = datetime.strptime(row['End Time'], '%Y-%m-%d %I:%M %p')

    # shift starts and ends on holiday -> Regular Hours
    if start_time.date() == holiday.date() and end_time.date() == holiday.date():
        return row[REGULAR_HOURS_WORKED]
    # shift starts on, ends after holiday -> smaller of Regular Hours or total hours on holiday
    elif start_time.date() == holiday.date() and end_time.date() > holiday.date():
        holiday_hours = delta_to_hours(holiday_end - start_time)
        holiday_hours = round(holiday_hours, 2)
        return min(row[REGULAR_HOURS_WORKED],  holiday_hours)
    # shift starts before, ends on holiday - >
    elif start_time.date() < holiday.date() and end_time.date() == holiday.date():
        overtime = row[OVERTIME_HOURS_WORKED]
        holiday_hours = delta_to_hours(end_time - holiday)
        holiday_hours = round(holiday_hours, 2)
        return max(holiday_hours - overtime,  0)
    # shift not on holiday -> 0
    else:
        return 0


def calc_holiday_pay(row) -> float:
    return round(row[PAY_RATE] * row[HOLIDAY_HOURS] * HOLIDAY_MULTIPLIER, 2)


def process_csv(holiday: datetime, csv_data: str) -> str:
    cols_to_keep = [CREATED_AT, NAME, START_TIME, END_TIME, LUNCH, HOURS_WORKED, REGULAR_HOURS_WORKED, OVERTIME_HOURS_WORKED, PAY_RATE, OVERTIME_PAY_RATE]
    df = pd.read_csv(StringIO(csv_data)).filter(cols_to_keep, axis=1)

    df[LUNCH] = df[LUNCH].fillna(0)
    df[HOLIDAY_HOURS] = df.apply(lambda row: calc_holiday_hours(holiday, row), axis=1)
    df[HOLIDAY_PAY] = df.apply(lambda row: calc_holiday_pay(row), axis=1)

    df.sort_values(CREATED_AT)
    df = df.drop(LUNCH, 1)
    df = df.drop(REGULAR_HOURS_WORKED, 1)
    df = df.drop(OVERTIME_PAY_RATE, 1)

    return df.to_csv()

