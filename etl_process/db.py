from etl_process.db_config import DRIVER_NAME, USERNAME, PASSWORD, HOST, PORT, DATABASE
import pandas as pd
from sqlalchemy.orm import sessionmaker
from model import F1Driver, F1Team, F1Event, F1Result, F1Weather, F1FIAControl, F1Lap, F1Telemetry
from sqlalchemy import create_engine, select, inspect
from sqlalchemy.engine import URL
# import logging
from model import Base


def make_db_session(
    drivername=DRIVER_NAME,
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
):
    try:
        url_object = URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        # print(f"Connection URL: {url_object}")
        engine = create_engine(url_object, echo=False, connect_args={"client_encoding": "utf8"})
        # Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session(), engine
    except Exception as e:
        print(f"Failed to create session: {e}")
        raise

def list_tables(engine):
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []


def check_or_create_driver(session, row):  # alternative approach like get or create
    try:        
        driver = session.query(F1Driver).filter_by(Abbreviation=row.Abbreviation).first()
        if driver:
            return None
        
        new_driver = F1Driver(
            Abbreviation=row.Abbreviation,
            FullName = row.FullName,
            DriverNumber = row.DriverNumber,
            CountryCode = row.CountryCode,
            HeadshotUrl = row.HeadshotUrl
        )

        session.add(new_driver)
        session.commit()
    except Exception as e:
        print(f"Query error: {e}")


def check_or_create_team(session, row):
    try:        
        team = session.query(F1Team).filter_by(TeamName=row.TeamName).first()
        if team:
            return None
        
        new_team = F1Team(
            TeamName=row.TeamName,
            TeamColor = row.TeamColor
        )

        session.add(new_team)
        session.commit()
    except Exception as e:
        print(f"Query error: {e}")   


def check_is_new_data_exist(session, meeting_key, session_key):
    
    # now we suggest if event table don't have specific values of meeting and session that means we don't have data by this at all
    event = session.query(F1Event).filter((F1Event.MeetingKey==meeting_key) & (F1Event.SessionKey==session_key)).first()
    if event:
        return 1
    return None


def load_to_db(event_df: pd.DataFrame, weather_df: pd.DataFrame, result_df: pd.DataFrame,
               fia_control_df: pd.DataFrame, driver_laps_df: pd.DataFrame, driver_telemetry_df: pd.DataFrame):
    try:
        session, engine = make_db_session()
        with session as session:
            
            for row in event_df.itertuples():
                meeting_key = row.MeetingKey
                session_key = row.SessionKey

                if check_is_new_data_exist(session, meeting_key, session_key):
                    continue
                
                # devide data into group by session
                temp_event_df = event_df[(event_df['MeetingKey']==meeting_key) & (event_df['SessionKey']==session_key)]
                temp_weather_df = weather_df[(weather_df['MeetingKey']==meeting_key) & (weather_df['SessionKey']==session_key)]
                temp_result_df = result_df[(result_df['MeetingKey']==meeting_key) & (result_df['SessionKey']==session_key)]
                temp_driver_lap_df = driver_laps_df[(driver_laps_df['MeetingKey']==meeting_key) & (driver_laps_df['SessionKey']==session_key)]
                # not have driver Abbreviation, only number
                temp_fia_control_df = fia_control_df[(fia_control_df['MeetingKey']==meeting_key) & (fia_control_df['SessionKey']==session_key)]
                temp_driver_telemetry_df = driver_telemetry_df[(driver_telemetry_df['MeetingKey']==meeting_key) & (driver_telemetry_df['SessionKey']==session_key)]

                temp_fia_control_df = temp_fia_control_df.merge(
                    temp_result_df[['DriverNumber', 'Abbreviation']],
                    how='left', left_on='RacingNumber', right_on='DriverNumber'
                    ).drop(columns=['RacingNumber', 'DriverNumber'])

                temp_driver_telemetry_df = temp_driver_telemetry_df.merge(
                    temp_result_df[['DriverNumber', 'Abbreviation']],
                    how='left', left_on='DriverNumber', right_on='DriverNumber'
                    ).drop(columns=['DriverNumber'])

                temp_fia_control_df.to_csv('changed_fia_control.csv', index=False)
                temp_driver_telemetry_df.to_csv('changed_driver_telemetry.csv', index=False)

                # check is driver or team from new data exist in db if not than write
                for row in temp_result_df.itertuples():
                    check_or_create_driver(session, row)
                    check_or_create_team(session, row)
                

                # making cache data
                driver_cache = {row.Abbreviation: row.id for row in session.execute(select(F1Driver.Abbreviation, F1Driver.id)).all()}
                team_cache = {row.TeamName: row.id for row in session.execute(select(F1Team.TeamName, F1Team.id)).all()}

                # insert data into tables
                # using bulk insert mappings to map keys from dictionaries with table class attributes
                # this version with handling pandas NaN values and datatype
                session.bulk_insert_mappings(F1Event, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey,
                        'Season': row.Season if pd.notna(row.Season) else None,
                        'WeekendNumber': row.WeekendNumber if pd.notna(row.WeekendNumber) else None,
                        'ShortName': row.ShortName if pd.notna(row.ShortName) else None,
                        'FullName': row.FullName if pd.notna(row.FullName) else None,
                        'CountryName': row.CountryName if pd.notna(row.CountryName) else None,
                        'LocationType': row.LocationType if pd.notna(row.LocationType) else None,
                        'CircuitName': row.CircuitName if pd.notna(row.CircuitName) else None,
                        'SessionType': row.SessionType if pd.notna(row.SessionType) else None,
                        'SessionName': row.SessionName if pd.notna(row.SessionName) else None,
                        'LocalStartDate': row.LocalStartDate if pd.notna(row.LocalStartDate) else None,
                        'LocalEndDate': row.LocalEndDate if pd.notna(row.LocalEndDate) else None,
                        'GMTStartDate': row.GMTStartDate if pd.notna(row.GMTStartDate) else None,
                        'GMTEndDate': row.GMTEndDate if pd.notna(row.GMTEndDate) else None
                    } for row in temp_event_df.itertuples()
                    ])

                session.bulk_insert_mappings(F1Weather, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey,
                        'Time': row.Time if pd.notna(row.Time) else None,
                        'AirTemp': row.AirTemp if pd.notna(row.AirTemp) else None, 
                        'Humidity': row.Humidity if pd.notna(row.Humidity) else None,
                        'Pressure': row.Pressure if pd.notna(row.Pressure) else None,
                        'Rainfall': row.Rainfall if pd.notna(row.Rainfall) else None,
                        'TrackTemp': row.TrackTemp if pd.notna(row.TrackTemp) else None,
                        'WindDirection': row.WindDirection if pd.notna(row.WindDirection) else None,
                        'WindSpeed': row.WindSpeed if pd.notna(row.WindSpeed) else None
                    } for row in temp_weather_df.itertuples()
                ])

                session.bulk_insert_mappings(F1Result, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey,
                        'DriverId': driver_cache.get(row.Abbreviation),
                        'TeamId': team_cache.get(row.TeamName),
                        'Position': int(row.Position) if pd.notna(row.Position) else None,
                        'ClassifiedPosition': row.ClassifiedPosition if pd.notna(row.ClassifiedPosition) else None,
                        'GridPosition': int(row.GridPosition) if pd.notna(row.GridPosition) else None,
                        'Q1': row.Q1 if pd.notna(row.Q1) else None,
                        'Q2': row.Q2 if pd.notna(row.Q2) else None,
                        'Q3': row.Q3 if pd.notna(row.Q3) else None,
                        'Time': row.Time if pd.notna(row.Time) else None,
                        'Status': row.Status if pd.notna(row.Status) else None,
                        'Points': row.Points if pd.notna(row.Points) else None,
                    } for row in temp_result_df.itertuples()
                ])

                session.bulk_insert_mappings(F1FIAControl, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey,
                        'DriverId': driver_cache.get(row.Abbreviation) if pd.notna(row.Abbreviation) else None,
                        'Time': row.Time if pd.notna(row.Time) else None,
                        'Lap': row.Lap if pd.notna(row.Lap) else None,
                        'Category': row.Category if pd.notna(row.Category) else None,
                        'Message': row.Message if pd.notna(row.Message) else None,
                        'Status': row.Status if pd.notna(row.Status) else None,
                        'Flag': row.Flag if pd.notna(row.Flag) else None,
                        'Scope': row.Scope if pd.notna(row.Scope) else None,
                        'Sector': row.Sector if pd.notna(row.Sector) else None
                    } for row in temp_fia_control_df.itertuples()
                ])

                session.bulk_insert_mappings(F1Lap, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey, 
                        'DriverId': driver_cache.get(row.Driver), 
                        'TeamId': team_cache.get(row.Team),
                        'Time': row.Time if pd.notna(row.Time) else None, 
                        'LapTime': row.LapTime if pd.notna(row.LapTime) else None,
                        'LapNumber': int(row.LapNumber) if pd.notna(row.LapNumber) else None,
                        'Stint': int(row.Stint) if pd.notna(row.Stint) else None, 
                        'PitOutTime': row.PitOutTime if pd.notna(row.PitOutTime) else None,
                        'PitInTime': row.PitInTime if pd.notna(row.PitInTime) else None,
                        'Sector1Time': row.Sector1Time if pd.notna(row.Sector1Time) else None,
                        'Sector2Time': row.Sector2Time if pd.notna(row.Sector2Time) else None,
                        'Sector3Time': row.Sector3Time if pd.notna(row.Sector3Time) else None,
                        'Sector1SessionTime': row.Sector1SessionTime if pd.notna(row.Sector1SessionTime) else None,
                        'Sector2SessionTime': row.Sector2SessionTime if pd.notna(row.Sector2SessionTime) else None,
                        'Sector3SessionTime': row.Sector3SessionTime if pd.notna(row.Sector3SessionTime) else None,
                        'SpeedI1': row.SpeedI1 if pd.notna(row.SpeedI1) else None,
                        'SpeedI2': row.SpeedI2 if pd.notna(row.SpeedI2) else None,
                        'SpeedFL': row.SpeedFL if pd.notna(row.SpeedFL) else None,
                        'SpeedST': row.SpeedST if pd.notna(row.SpeedST) else None,
                        'IsPersonalBest': row.IsPersonalBest if pd.notna(row.IsPersonalBest) else None,
                        'Compound': row.Compound if pd.notna(row.Compound) else None,
                        'TyreLife': int(row.TyreLife) if pd.notna(row.TyreLife) else None,
                        'FreshTyre': row.FreshTyre if pd.notna(row.FreshTyre) else None,
                        'LapStartTime': row.LapStartTime if pd.notna(row.LapStartTime) else None,
                        'LapStartDate': row.LapStartDate if pd.notna(row.LapStartDate) else None,
                        'TrackStatus': int(row.TrackStatus) if pd.notna(row.TrackStatus) else None,
                        'Position': int(row.Position) if pd.notna(row.Position) else None,
                        'Deleted': row.Deleted if pd.notna(row.Deleted) else None,
                        'DeletedReason': row.DeletedReason if pd.notna(row.DeletedReason) else None,
                        'FastF1Generated': row.FastF1Generated if pd.notna(row.FastF1Generated) else None,
                        'IsAccurate': row.IsAccurate if pd.notna(row.IsAccurate) else None
                    } for row in temp_driver_lap_df.itertuples()
                ])

                session.bulk_insert_mappings(F1Telemetry, [
                    {
                        'MeetingKey': row.MeetingKey,
                        'SessionKey': row.SessionKey,
                        'DriverId': driver_cache.get(row.Abbreviation),
                        'Date': row.Date if pd.notna(row.Date) else None, 
                        'RPM': row.RPM if pd.notna(row.RPM) else None,
                        'Speed': row.Speed if pd.notna(row.Speed) else None,
                        'nGear': row.nGear if pd.notna(row.nGear) else None,
                        'Throttle': row.Throttle if pd.notna(row.Throttle) else None,
                        'Brake': row.Brake if pd.notna(row.Brake) else None,
                        'DRS': row.DRS if pd.notna(row.DRS) else None,
                        'Time': row.Time if pd.notna(row.Time) else None,
                        'SessionTime': row.SessionTime if pd.notna(row.SessionTime) else None,
                        'Distance': row.Distance if pd.notna(row.Distance) else None,
                        'LapNumber': row.LapNumber if pd.notna(row.LapNumber) else None
                    } for row in temp_driver_telemetry_df.itertuples()
                ])

                session.commit()

    except Exception as e:
        print(f"Main error: {e}")
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    make_db_session()