import pandas as pd
import numpy as np
from datetime import datetime


def convert_timedelta_into_datetime(df: pd.DataFrame, col: str, basedate: datetime):
    if col in df.columns:
        return df[col].apply(lambda time: pd.to_datetime(basedate+time).time() if pd.notna(time) else np.nan)
    else:
        return None
    

def transform_weather_data(df: pd.DataFrame, basedate=datetime(2025, 4, 1)):
    # using tricky method to convert timedelta into datetime
    df['Time'] = convert_timedelta_into_datetime(df, 'Time', basedate)
    return df


def transform_fia_control_data(df: pd.DataFrame):
    return df


def transform_result_data(df: pd.DataFrame, basedate=datetime(2025, 4, 1)):
    df['HeadshotUrl'] = df['HeadshotUrl'].str.replace('.transform/1col/image.png', '')
    df['Q1'] = convert_timedelta_into_datetime(df, 'Q1', basedate)
    df['Q2'] = convert_timedelta_into_datetime(df, 'Q2', basedate)
    df['Q3'] = convert_timedelta_into_datetime(df, 'Q3', basedate)
    df['Time'] = convert_timedelta_into_datetime(df, 'Time', basedate)
    return df


def transform_lap_data(df: pd.DataFrame, basedate=datetime(2025, 4, 1)):
    # convert all timedelta data into datetime
    df['Time'] = convert_timedelta_into_datetime(df, 'Time', basedate)
    df['LapTime'] = convert_timedelta_into_datetime(df, 'LapTime', basedate)
    df['PitOutTime'] = convert_timedelta_into_datetime(df, 'PitOutTime', basedate)
    df['PitInTime'] = convert_timedelta_into_datetime(df, 'PitInTime', basedate)
    df['Sector1Time'] = convert_timedelta_into_datetime(df, 'Sector1Time', basedate)
    df['Sector2Time'] = convert_timedelta_into_datetime(df, 'Sector2Time', basedate)
    df['Sector3Time'] = convert_timedelta_into_datetime(df, 'Sector3Time', basedate)
    df['Sector1SessionTime'] = convert_timedelta_into_datetime(df, 'Sector1SessionTime', basedate)
    df['Sector2SessionTime'] = convert_timedelta_into_datetime(df, 'Sector2SessionTime', basedate)
    df['Sector3SessionTime'] = convert_timedelta_into_datetime(df, 'Sector3SessionTime', basedate)
    df['LapStartTime'] = convert_timedelta_into_datetime(df, 'LapStartTime', basedate)
    return df


def transform_telemetry_data(df: pd.DataFrame, basedate=datetime(2025, 4, 1)):
    df['Time'] = convert_timedelta_into_datetime(df, 'Time', basedate)
    df['SessionTime'] = convert_timedelta_into_datetime(df, 'SessionTime', basedate)
    return df