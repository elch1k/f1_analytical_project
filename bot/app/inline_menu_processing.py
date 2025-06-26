from sqlalchemy.ext.asyncio import AsyncSession
from app.keyboards import (
    get_f1_seasons_kb,
    get_f1_gps_kb,
    get_f1_sessions_kb,
    get_f1_analytical_functions_kb,
    get_seasonal_menu_kb,
    main_start_kb,
    back_to_main_button
    )
from utils.orm_queries import (
    get_f1_seasons,
    get_f1_grand_prix,
    get_f1_weekend_session
    )

from app.analytical_plots import (
    get_weather_report_plot,
    get_race_tyre_strategy_plot,
    get_drivers_race_pace,
    get_race_results_table
)


async def get_main_static_menu(level):
    kb = await main_start_kb(level)
    message_text = "Hi there! Welcome to the F1 analytical bot MVP. What statistic are you most interested in?"

    return message_text, kb


async def get_historical_menu(level, prev_sub_level):
    kb = await back_to_main_button(level, prev_sub_level)
    message_text = "Oops! This function isn't quite ready yet. I'm working on it!"

    return message_text, kb


async def get_about_project_section(level, prev_sub_level):
    kb = await back_to_main_button(level, prev_sub_level)
    message_text = (
    "🏎️ Formula 1 Analytical Bot\n"
    "This bot analyzes F1 statistics to provide unique insights into the world of Formula 1.\n"
    "It's a non-commercial, open-source project aimed at making F1 data easily accessible.\n\n"
    "📂 Source Code: https://github.com/elch1k/f1_analytical_project\n"
    "📬 Contact: @nesterenk0d"
    )

    return message_text, kb


async def get_seasonal_menu(level, sub_level, previous_sub_level):
    kb = await get_seasonal_menu_kb(level, sub_level, previous_sub_level)
    message_text = "Which season's statistics are you interested in?"

    return message_text, kb


async def get_summary_seasonal_stat(level, prev_sub_level):
    kb = await back_to_main_button(level, prev_sub_level)
    message_text = "Oops! This function isn't quite ready yet. I'm working on it!"

    return message_text, kb


async def get_season_menu(session, level, prev_sub_level):
    seasons = await get_f1_seasons(session)
    kb = await get_f1_seasons_kb(seasons, level, prev_sub_level)
    message_text = 'Select an F1 season:'

    return message_text, kb


async def get_gp_menu(session, level, season):
    gps = await get_f1_grand_prix(session, season)
    kb = await get_f1_gps_kb(gps, season, level)
    message_text = 'Select a Grand Prix:'

    return message_text, kb


async def get_weekend_session_menu(session, level, gp, season):
    weekend_sessions = await get_f1_weekend_session(session, gp, season)
    kb = await get_f1_sessions_kb(weekend_sessions, gp, season, level)
    message_text = 'Select a weekend session:'

    return message_text, kb


async def get_analytical_function_menu(level, weekend_session, gp, season):
    kb = await get_f1_analytical_functions_kb(weekend_session, gp, season, level)
    message_text = 'Available analytical reports:'

    return message_text, kb


async def get_menu_content(
    session: AsyncSession,
    level: int,
    sub_level: str | None = None,
    prev_sub_level: str | None = None,
    season: int | None = None,
    gp: str | None = None,
    weekend_session: str | None = None,
    analytical_function: str | None = None
):
    if level == 0:
        return await get_main_static_menu(level)
    elif level == 1 and sub_level == 'hist_stat':
        return await get_historical_menu(level, prev_sub_level)
    elif level == 1 and sub_level == 'about':
        return await get_about_project_section(level, prev_sub_level)
    elif level == 1 and sub_level == 'seas_stat':
        return await get_seasonal_menu(level, sub_level, prev_sub_level)
    elif level == 2 and sub_level == 'seas_overview':
        return await get_summary_seasonal_stat(level, prev_sub_level)
    elif level == 2 and sub_level == 'gp_stat':
        return await get_season_menu(session, level, prev_sub_level)
    elif level == 3:
        return await get_gp_menu(session, level, season)
    elif level == 4:
        return await get_weekend_session_menu(session, level, gp, season)
    elif level == 5:
        return await get_analytical_function_menu(level, weekend_session, gp, season)
    elif level == 6:
        if analytical_function == 'weather':
            return await get_weather_report_plot(session, weekend_session, gp, season)
        if analytical_function == 'tyre_strat':
            return await get_race_tyre_strategy_plot(session, weekend_session, gp, season)
        if analytical_function == 'drivers_pace':
            return await get_drivers_race_pace(session, weekend_session, gp, season)
        if analytical_function == 'res':
            return await get_race_results_table(session, weekend_session, gp, season)
