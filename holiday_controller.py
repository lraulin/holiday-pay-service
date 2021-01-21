import pandas as pd
from dateparser import parse
from datetime import datetime, timedelta
from io import BytesIO, StringIO

HOLIDAY_MULTIPLIER = 0.5

# Column Headers
CREATED_AT = 'Created At (UTC)'
HOURS_WORKED = 'Hours Worked'
HOLIDAY_HOURS = 'HOL'
HOLIDAY_PAY = 'Adjustment'
LUNCH = 'Lunch (in mins)'
NON_HOLIDAY_HOURS = 'X-Non-holiday Hours'
NON_HOLIDAY_PAY = 'X-Non-Holiday Pay'
TOTAL_PAY = 'Total Pay'
START_TIME = 'Start Time'
END_TIME = 'End Time'
NAME = 'Name'
## Pay Rates
PAY_RATE = 'Pay Rate'
OVERTIME_PAY_RATE = 'Overtime Pay Rate'
DOUBLETIME_RATE = 'Doubletime Pay Rate'
STIPEND = 'Stipend (Pro-rated)'
## Hours
REGULAR_HOURS_WORKED = 'Regular Hours Worked'
OVERTIME_HOURS_WORKED = 'Overtime Hours Worked'
DOUBLETIME_HOURS_WORKED = 'Doubletime Hours Worked'


def delta_to_hours(delta: timedelta):
    seconds_in_hour = 3600
    return delta.seconds / seconds_in_hour


def calc_holiday_hours(holiday: datetime, row) -> float:
    holiday_end = holiday + timedelta(days=1)
    start_time = parse(row['Start Time'])
    end_time = parse(row['End Time'])


    # shift starts and ends on holiday -> Regular Hours
    if start_time.date() == holiday.date() and end_time.date() == holiday.date():
        return row[REGULAR_HOURS_WORKED]
    # shift starts on, ends after holiday -> smaller of Regular Hours or total hours on holiday
    elif start_time.date() == holiday.date() and end_time.date() > holiday.date():
        holiday_hours = delta_to_hours(holiday_end - start_time)
        holiday_hours = round(holiday_hours, 2)
        return min(row[REGULAR_HOURS_WORKED], holiday_hours)
    # shift starts before, ends on holiday - >
    elif start_time.date() < holiday.date() and end_time.date() == holiday.date():
        overtime = row[OVERTIME_HOURS_WORKED] + row[DOUBLETIME_HOURS_WORKED]
        hours_worked_on_holiday = round(delta_to_hours(end_time - holiday), 2)
        adjustment_hours = max(hours_worked_on_holiday - overtime, 0)
        adjustment_hours = min(row[REGULAR_HOURS_WORKED], adjustment_hours)
        return adjustment_hours
    # shift not on holiday -> 0
    else:
        return 0


def calc_holiday_pay(row) -> float:
    return round(row[PAY_RATE] * row[HOLIDAY_HOURS] * HOLIDAY_MULTIPLIER, 2)


def calc_total_pay(row):
    return round(row[PAY_RATE] * row[REGULAR_HOURS_WORKED] + row[OVERTIME_PAY_RATE] * row[OVERTIME_HOURS_WORKED] + row[
        DOUBLETIME_RATE] * row[DOUBLETIME_HOURS_WORKED] + row[STIPEND] + row[HOLIDAY_PAY], 2)


def process_csv(holiday: datetime, csv_data: str, save=False) -> dict:
    cols_to_keep = [CREATED_AT, NAME, START_TIME, END_TIME, LUNCH, HOURS_WORKED, REGULAR_HOURS_WORKED,
                    OVERTIME_HOURS_WORKED, PAY_RATE, OVERTIME_PAY_RATE, DOUBLETIME_HOURS_WORKED, DOUBLETIME_RATE,
                    STIPEND]
    df = pd.read_csv(StringIO(csv_data)).filter(cols_to_keep, axis=1)

    # Fill missing number cells with 0
    df[LUNCH] = df[LUNCH].fillna(0)
    df[PAY_RATE] = df[PAY_RATE].fillna(0)
    df[REGULAR_HOURS_WORKED] = df[REGULAR_HOURS_WORKED].fillna(0)
    df[OVERTIME_PAY_RATE] = df[OVERTIME_PAY_RATE].fillna(0)
    df[OVERTIME_HOURS_WORKED] = df[OVERTIME_HOURS_WORKED].fillna(0)
    df[DOUBLETIME_RATE] = df[DOUBLETIME_RATE].fillna(0)
    df[DOUBLETIME_HOURS_WORKED] = df[DOUBLETIME_HOURS_WORKED].fillna(0)

    # Add calculated columns
    df[HOLIDAY_HOURS] = df.apply(lambda row: calc_holiday_hours(holiday, row), axis=1)
    df[HOLIDAY_PAY] = df.apply(lambda row: calc_holiday_pay(row), axis=1)
    df[TOTAL_PAY] = df.apply(lambda row: calc_total_pay(row), axis=1)

    df = df[[CREATED_AT, NAME, START_TIME, END_TIME, HOURS_WORKED, OVERTIME_HOURS_WORKED, PAY_RATE, HOLIDAY_HOURS, HOLIDAY_PAY, TOTAL_PAY]]
    df.sort_values(CREATED_AT)

    # Find entries needing admin approval
    needs_super_admin = df[TOTAL_PAY] >= 2000
    names_needing_approval = list(set(df[needs_super_admin][NAME]))

    # for debugging
    if save:
        df.to_csv('output.csv')

    return {'csv': df.to_csv(), 'super_admin_list': names_needing_approval}

# if __name__ == '__main__':
#     date = datetime(year=2021, month=1, day=1)
#     file = '/Users/leeraulin/Dropbox/My Mac (Lees-MBP.ad.dot.gov)/Downloads/Timecards-Export-2021-01-21-12-37-15.txt'
#     # file = '/Users/leeraulin/Dropbox/My Mac (Lees-MBP.ad.dot.gov)/Downloads/Timecards-Export-2021-01-18-12-17-33.txt'
#     with open(file, 'r') as file:
#         data = file.read()
#         process_csv(date, data, True)
#
