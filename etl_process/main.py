from parse_functions import get_f1_data_from_api
from data_transform import (transform_weather_data,transform_lap_data,
                            transform_fia_control_data,transform_result_data,
                            transform_telemetry_data)
from db import load_to_db
import pandas as pd
import time
import random


def save_to_datalake(event_df: pd.DataFrame, weather_df: pd.DataFrame, result_df: pd.DataFrame,
                     fia_control_df: pd.DataFrame, driver_laps_df: pd.DataFrame, driver_telemetry_df: pd.DataFrame) -> None:
    
    # save original raw data into datalake
    event_df.to_csv('raw_datalake/f1_event.csv', index=False)
    weather_df.to_csv('raw_datalake/f1_weather.csv', index=False)
    fia_control_df.to_csv('raw_datalake/f1_fia_control.csv', index=False)
    driver_laps_df.to_csv('raw_datalake/f1_driver_laps.csv', index=False)
    result_df.to_csv('raw_datalake/f1_result.csv', index=False)
    driver_telemetry_df.to_csv('raw_datalake/f1_driver_lap_telemetry.csv', index=False)


if __name__=="__main__":
    event_df, weather_df, result_df, fia_control_df, driver_laps_df, driver_telemetry_df = get_f1_data_from_api()

    save_to_datalake(event_df, weather_df, result_df, fia_control_df, driver_laps_df, driver_telemetry_df)

    transformed_weather_df = transform_weather_data(weather_df)
    transformed_fia_control_df = transform_fia_control_data(fia_control_df)
    transformed_driver_laps_df = transform_lap_data(driver_laps_df)
    transformed_result_df = transform_result_data(result_df)
    transformed_telemetry_df = transform_telemetry_data(driver_telemetry_df)

    load_to_db(
        event_df,
        transformed_weather_df,
        transformed_result_df,
        transformed_fia_control_df,
        transformed_driver_laps_df,
        transformed_telemetry_df
    )