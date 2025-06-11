import fastf1 as ff1
import pandas as pd
from datetime import datetime
import time
import random


def get_f1_weekend_event_name(year: int, weekend_num: int, weekend_session: int):
    try:
        f1_weekend_event_name = ff1.get_session(year, weekend_num, weekend_session)
    except Exception as e:
        print(e)  # need to add logging
        return None
    else:
        return f1_weekend_event_name


def get_weekend_event_data(weekend_event_name, weekend, year):
    weekend_session = weekend_event_name.session_info
    meeting_key = weekend_session.get("Meeting").get("Key")

    session_key = weekend_session.get("Key")
    session_type = weekend_session.get("Type")
    session_name = weekend_session.get("Name")

    local_start_date = weekend_session.get("StartDate")
    local_end_date = weekend_session.get("EndDate")
    gmt_offset = weekend_session.get("GmtOffset")
    gmt_start_date = local_start_date - gmt_offset
    gmt_end_date = local_end_date - gmt_offset

    df = pd.DataFrame({
        "MeetingKey": [meeting_key],
        "SessionKey": [session_key],
        "Season": [year],
        "WeekendNumber": [weekend],
        "ShortName": [weekend_session.get("Meeting").get("Name")],
        "FullName": [weekend_session.get("Meeting").get("OfficialName")],
        # "CountryId": [weekend_session.get("Meeting").get("Country").get("Key")],
        "CountryName": [weekend_session.get("Meeting").get("Country").get("Name")],
        "LocationType": [weekend_session.get("Meeting").get("Location")],
        # "CircuitId": [weekend_session.get("Meeting").get("Circuit").get("Key")],
        "CircuitName": [weekend_session.get("Meeting").get("Circuit").get("ShortName")],
        "SessionType": [session_type],
        "SessionName": [session_name],
        "LocalStartDate": [local_start_date],
        "LocalEndDate": [local_end_date],
        "GMTStartDate": [gmt_start_date],
        "GMTEndDate": [gmt_end_date]
    })

    return df, meeting_key, session_key, session_type


def add_meeting_and_session_key(df, meeting_key, session_key):
    df["MeetingKey"] = meeting_key
    df["SessionKey"] = session_key
    return df


def get_session_weather_data(meeting_key: int, session_key: int, weekend_event_name):
    df = weekend_event_name.weather_data
    df = add_meeting_and_session_key(df, meeting_key, session_key)
    return df[['MeetingKey', 'SessionKey', 'Time', 'AirTemp', 'Humidity',
               'Pressure', 'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed']]


def get_session_result_data(meeting_key: int, session_key: int, weekend_event_name):
    df = weekend_event_name.results
    df = add_meeting_and_session_key(df, meeting_key, session_key)
    return df[['MeetingKey', 'SessionKey', 'Abbreviation', 'FullName',
               'DriverNumber', 'CountryCode', 'TeamName', 'TeamColor',
               'HeadshotUrl','Position', 'ClassifiedPosition',
               'GridPosition', 'Q1', 'Q2', 'Q3', 'Time', 'Status', 'Points']]


def get_session_laps_data(meeting_key: int, session_key: int, weekend_event_name):
    df = weekend_event_name.laps
    df = add_meeting_and_session_key(df, meeting_key, session_key)
    return df[['MeetingKey', 'SessionKey', 'Time', 'Driver', 'DriverNumber',
               'LapTime', 'LapNumber', 'Stint', 'PitOutTime', 'PitInTime',
               'Sector1Time', 'Sector2Time', 'Sector3Time', 'Sector1SessionTime',
               'Sector2SessionTime', 'Sector3SessionTime', 'SpeedI1', 'SpeedI2',
               'SpeedFL', 'SpeedST', 'IsPersonalBest', 'Compound', 'TyreLife',
               'FreshTyre', 'Team', 'LapStartTime', 'LapStartDate', 'TrackStatus',
               'Position', 'Deleted', 'DeletedReason', 'FastF1Generated', 'IsAccurate']]


def get_session_fia_control_data(meeting_key: int, session_key: int, weekend_event_name):
    df = weekend_event_name.race_control_messages
    df = add_meeting_and_session_key(df, meeting_key, session_key)
    return df[['MeetingKey', 'SessionKey', 'Time', 'Lap', 'Category',
               'Message', 'Status', 'Flag', 'Scope', 'Sector', 'RacingNumber']]


def get_laps_telemetry(weekend_event_name, drivers_number, meeting_key, session_key):  # session_type
    full_telemetry_df = pd.DataFrame()
    for number in drivers_number:
        driver_laps = weekend_event_name.laps.pick_driver(number)

        lap_counter = 1
        for lap in driver_laps.iterlaps():
            try:
                detail_laps_telemetry_df = lap[1].get_car_data().add_distance()  # .add_driver_ahead()
            # add additional info about what driver ahead and what distance between them (use only for race)
            except Exception as e:
                lap_counter+=1
                continue
            detail_laps_telemetry_df["DriverNumber"] = number
            detail_laps_telemetry_df["LapNumber"] = lap_counter
            detail_laps_telemetry_df["MeetingKey"] = meeting_key
            detail_laps_telemetry_df["SessionKey"] = session_key

            lap_counter+=1
            full_telemetry_df = pd.concat([full_telemetry_df, detail_laps_telemetry_df], axis=0)
    return full_telemetry_df[['MeetingKey', 'SessionKey', 'Date', 'RPM', 'Speed',
                            'nGear', 'Throttle', 'Brake', 'DRS', 'Time',
                            'SessionTime', 'Distance', 'DriverNumber', 'LapNumber']]


def get_f1_data_from_api():
    full_event_df = pd.DataFrame()
    full_result_df = pd.DataFrame()
    full_weather_df = pd.DataFrame()
    full_driver_laps_df = pd.DataFrame()
    full_driver_telemetry_df = pd.DataFrame()
    full_fia_control_df = pd.DataFrame()

    for year in range(2025, 2026):
        for weekend in range(1, 2):
            for weekend_event in range(5, 6):
                weekend_event_name = get_f1_weekend_event_name(year, weekend, weekend_event)
                if not weekend_event_name:
                    continue

                weekend_event_name.load()

                session_info_df, meeting_key, session_key, session_type = get_weekend_event_data(weekend_event_name, weekend, year)
                session_weather_df = get_session_weather_data(meeting_key, session_key, weekend_event_name)
                session_results_df = get_session_result_data(meeting_key, session_key, weekend_event_name)
                
                session_laps_df = get_session_laps_data(meeting_key, session_key, weekend_event_name)
                session_fia_control_message = get_session_fia_control_data(meeting_key, session_key, weekend_event_name)

                if session_type != "Practice":
                    drivers_number_by_session = session_results_df["DriverNumber"].unique()
                    driver_full_telemetry_df = get_laps_telemetry(weekend_event_name, drivers_number_by_session, meeting_key, session_key)
                else:
                    driver_full_telemetry_df = pd.DataFrame()

                # concatenation
                full_event_df = pd.concat([full_event_df, session_info_df], axis=0)
                full_result_df = pd.concat([full_result_df, session_results_df], axis=0)
                full_weather_df = pd.concat([full_weather_df, session_weather_df], axis=0)
                full_driver_laps_df = pd.concat([full_driver_laps_df, session_laps_df], axis=0)
                full_driver_telemetry_df = pd.concat([full_driver_telemetry_df, driver_full_telemetry_df], axis=0)
                full_fia_control_df = pd.concat([full_fia_control_df, session_fia_control_message], axis=0)

                # not to get banned
                time.sleep(random.randint(8, 15))

    return full_event_df, full_weather_df, full_result_df, full_fia_control_df, full_driver_laps_df, full_driver_telemetry_df


if __name__=='__main__':
    get_f1_data_from_api()