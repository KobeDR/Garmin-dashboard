import pandas as pd
from calendar import monthrange
from datetime import datetime
from data.cache import load, save
from garminconnect import Garmin
import streamlit as st

def get_client(email, password):
    client = Garmin(email, password)
    client.login()
    return client

def get_day_hr_data(date, _client, email):
    day = date.day
    year = date.year
    month = date.month
    day_today = datetime.today().day
    year_today = datetime.today().year
    month_today = datetime.today().month
    if month<10:
        month = f'0{month}'
    if day<10:
        day = f'0{day}'
    
    if month_today<10:
        month_today = f'0{month_today}'
    if day_today<10:
        day_today = f'0{day_today}'
    date_ref = f"{year}-{month}-{day}"
    date_today = f"{year_today}-{month_today}-{day_today}"
    hr =  _client.get_heart_rates(date_ref)
    hr_df = pd.DataFrame((hr['heartRateValues']), columns = ['Timepoint', 'HR'])
    return hr_df
    
# def get_day_sleep_hr_data(date, _client, email):
#     day = date.day
#     year = date.year
#     month = date.month
#     if month<10:
#         month = f'0{month}'
#     if day<10:
#         day = f'0{day}'
#     date_ref = f"{year}-{month}-{day}"
#     df = load(f'{date_ref}_sleephr', email)
#     if isinstance(df, bool):
#         sleep =  _client.get_sleep_data(date_ref)
#         try:
#             Timepoint= [i['startGMT'] for i in sleep['sleepHeartRate']]
#         except:
#             return False
#         HR = [i['value'] for i in sleep['sleepHeartRate']]
#         hr_df = pd.DataFrame({'Timepoint':Timepoint, 'HR':HR})
#         save(f'{date_ref}_sleephr', hr_df, email)
#         return hr_df
#     return df

def get_day_stress_data(date, _client, email):
    day = date.day
    year = date.year
    month = date.month
    day_today = datetime.today().day
    year_today = datetime.today().year
    month_today = datetime.today().month
    if month<10:
        month = f'0{month}'
    if day<10:
        day = f'0{day}'
    
    if month_today<10:
        month_today = f'0{month_today}'
    if day_today<10:
        day_today = f'0{day_today}'
    date_ref = f"{year}-{month}-{day}"
    date_today = f"{year_today}-{month_today}-{day_today}"


    stress = _client.get_stress_data(date_ref)
    stress_df = pd.DataFrame((stress['stressValuesArray']), columns = ['Timepoint', 'Stress'])
    return stress_df

def get_year_data(year, _client, email):
    year = int(year)
    
    """Download all Garmin stats for a given year."""
    df= load(year, email)
    if isinstance(df, bool):
        rows = []

        for month in range(1, 13):

            num_days = monthrange(year, month)[1]
            if month<10:
                month = f'0{month}'
            for day in range(1, num_days + 1):
                if day<10:
                    day = f'0{day}'
                date = f"{year}-{month}-{day}"
                try:
                    stats = _client.get_stats(date)

                    # Add the date as an explicit column
                    stats["date"] = pd.to_datetime(date)
                    stats["month"] = month

                    rows.append(stats)

                except Exception as e:
                    print(f"Error fetching {date}: {e}")

        df = pd.DataFrame(rows)
        save(year, df, email)
    

    return df