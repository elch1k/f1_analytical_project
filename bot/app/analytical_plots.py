from utils.model import F1Weather
# from etl_process.model import F1Weather
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import pandas as pd
import numpy as np
from aiogram.types import BufferedInputFile

from utils.orm_queries import (
    get_f1_weather_report,
    get_f1_session_start,
    get_f1_session_key,
    get_f1_session_driver,
    get_f1_race_tyres_data,
    get_f1_laptime,
    get_f1_race_results
    )


async def get_weather_report_plot(session, weekend_session, gp, season):
    weather_dict = {
        "Air temperature": F1Weather.AirTemp,
        "Humidity": F1Weather.Humidity,
        "Pressure": F1Weather.Pressure,
        "Track temperature": F1Weather.TrackTemp,
        "Wind speed (m/s)": F1Weather.WindSpeed,
        "Wind direction": F1Weather.WindDirection
    }
    
    session_key = await get_f1_session_key(session, weekend_session, gp, season)

    start, end = await get_f1_session_start(session,session_key)
    start_time = start.hour * 3600 + start.minute * 60 + start.second + start.microsecond / 1_000_000
    end_time = end.hour * 3600 + end.minute * 60 + end.second + end.microsecond / 1_000_000

    fig, axes = plt.subplots(3, 2, figsize=(12, 9))
    axes = axes.flatten()
    for ax, (weather_type, weather_model_value) in zip(axes, weather_dict.items()):

        result_values = await get_f1_weather_report(session, weather_model_value, session_key)
        weather_data, timings = zip(*result_values)
        seconds = [t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000 for t in timings]
        ax.plot(seconds, weather_data, label=weather_type)
        ax.axvline(x=start_time, color="red", linestyle="--", label="Session Start")
        ax.axvline(x=end_time, color="red", linestyle="--", label="Session End")

        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel(weather_type)
        ax.legend(loc='upper center',
                    bbox_to_anchor=(0.5, -0.105),
                    fancybox=True,
                    shadow=True,
                    ncol=5
                    )
        ax.set_title(f"{weather_type} over session")

    fig.suptitle(f"Weather conditions during {gp} - {weekend_session}", fontsize=16)
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)

    final_plot = BufferedInputFile(file=img_buffer.read(), filename="weather.png")
    plt.close()
    img_buffer.close()

    caption = 'Weather Report!'
    return (final_plot, caption)


async def get_race_tyre_strategy_plot(session, weekend_session, gp, season): 
    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#39B54A',
        'WET': '#00AEEF',
    }
    
    session_key = await get_f1_session_key(session, weekend_session, gp, season)
    tyres_data = await get_f1_race_tyres_data(session, session_key)
    session_driver = await get_f1_session_driver(session, session_key)

    tyres_df = pd.DataFrame(tyres_data, columns=['Driver', 'Stint', 'Compound', 'LapNumber'])
    fig, ax = plt.subplots()
    for driver in session_driver:
        driver_stint = tyres_df[tyres_df['Driver'] == driver]
        previous_stint_end = 0

        for _, stint in driver_stint.iterrows():
            plt.barh(
                [driver],
                stint['LapNumber'],
                left=previous_stint_end,
                color=compound_colors.get(stint['Compound' ]),
                edgecolor = 'black'
            )

            previous_stint_end = previous_stint_end + stint['LapNumber']
            plt.title(f'Tyre strategy: weekend {weekend_session}')

            plt.xlabel('Lap')
            plt.gca().invert_yaxis()

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)

    final_plot = BufferedInputFile(file=img_buffer.read(), filename="tyre_strategy.png")
    plt.close()
    img_buffer.close()

    caption = 'Race Tyre Strategy Report!'
    return (final_plot, caption)


async def get_drivers_race_pace(session, weekend_session, gp, season):
    # should sort drivers by finish position and remove laps under safety car
    session_key = await get_f1_session_key(session, weekend_session, gp, season)
    data = await get_f1_laptime(session, session_key)
    lap_time, driver, team_color = zip(*data)
    lap_time = [t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
            if t is not None else None
            for t in lap_time]

    df = pd.DataFrame({
        'LapTime': lap_time,
        'Driver': driver,
        'TeamColor': team_color
    })

    q75, q25 = df["LapTime"].quantile(0.75), df["LapTime"].quantile(0.25)

    intr_qr = q75 - q25
    laptime_max = q75 + (1.5 * intr_qr)
    laptime_min = q25 - (1.5 * intr_qr)

    df.loc[df['LapTime'] < laptime_min, 'LapTime'] = np.nan
    df.loc[df['LapTime'] > laptime_max, 'LapTime'] = np.nan
    
    driver_team_colors = dict(zip(df["Driver"], "#" + df["TeamColor"]))
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        x="Driver", y="LapTime", data=df,
        palette=driver_team_colors
    )

    plt.xlabel("Driver")
    plt.ylabel("Lap Time (seconds)")
    plt.title("Distribution of Lap Times by Driver")
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)

    final_plot = BufferedInputFile(file=img_buffer.read(), filename="drivers_race_pace.png")
    plt.close()
    img_buffer.close()

    caption = 'Drivers race pace through the race!'
    return (final_plot, caption)


async def get_race_results_table(session, weekend_session, gp, season):
    # should change tabel structure and work on ui design of dataframe
    session_key = await get_f1_session_key(session, weekend_session, gp, season)

    result = await get_f1_race_results(session, session_key)

    df = pd.DataFrame(result, columns=['NO', 'Driver', 'Grid Position', 'Finish Position', 'Time'])

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='left')

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')
        else:
            cell.set_facecolor('#f1f1f2')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)

    final_plot = BufferedInputFile(file=img_buffer.read(), filename="race_results.png")
    plt.close()
    img_buffer.close()

    caption = 'Race results report!'
    return (final_plot, caption)
    

