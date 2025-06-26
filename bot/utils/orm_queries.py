from utils.model import F1Event, F1Weather, F1Lap, F1Driver, F1Result, F1Team
# from etl_process.model import F1Event, F1Weather, F1Lap, F1Driver, F1Result, F1Team
from sqlalchemy import select, distinct, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession


# неявний join робить cross join
async def get_f1_seasons(session: AsyncSession):
    query = select(F1Event.Season).distinct()
    result = await session.execute(query)
    
    return result.scalars().all()


async def get_f1_grand_prix(session: AsyncSession, season: int):
    query = select(F1Event.ShortName).where(F1Event.Season==season).distinct()
    result = await session.execute(query)
    
    return result.scalars().all()


async def get_f1_weekend_session(session: AsyncSession, gp: str,  season: int):
    query = select(F1Event.SessionName).where(
            F1Event.Season==season,
            F1Event.ShortName==gp
        )
    result = await session.execute(query)

    return result.scalars().all()


async def get_f1_weather_report(session: AsyncSession, weather_value, session_key):
    second_qeury = select(weather_value, F1Weather.Time).where(
        F1Weather.SessionKey==session_key
        )
    result = await session.execute(second_qeury)
    return result.all()


async def get_f1_session_key(session: AsyncSession, weekend_session: str, gp: str, season: int):
    query = select(F1Event.SessionKey).where(
        F1Event.Season==season,
        F1Event.ShortName==gp,
        F1Event.SessionName==weekend_session
    )
    result = await session.execute(query)
    return result.scalars().all()[0]


async def get_f1_session_start(session: AsyncSession, session_key: int):
    max_value = select(func.max(F1Lap.Time)).where(
        F1Lap.SessionKey==session_key
    )
    min_value = select(func.min(F1Lap.Time)).where(
        F1Lap.SessionKey==session_key
    )
    max_result = await session.execute(max_value)
    min_result = await session.execute(min_value)
    
    return (max_result.scalars().all()[0], min_result.scalars().all()[0])


async def get_f1_race_tyres_data(session, session_key):
    query = (
        select(
            F1Driver.Abbreviation,
            F1Lap.Stint,
            F1Lap.Compound,
            func.count(F1Lap.LapNumber).label("lap_count")
        )
        .join(F1Lap.lap_driver)
        .where(F1Lap.SessionKey == session_key)
        .group_by(
            F1Driver.Abbreviation,
            F1Lap.Stint,
            F1Lap.Compound
        )
        .order_by(F1Lap.Stint)
    )

    result = await session.execute(query)
    rows = result.all()
    return rows


async def get_f1_session_driver(session, session_key):
    query = (
        select(
            F1Driver.Abbreviation
        )
        .join(F1Result.result_driver)
        .where(F1Result.SessionKey==session_key)
        .order_by(desc(F1Result.Position))
    )
    result = await session.execute(query)

    return result.scalars().all()


async def get_f1_laptime(session, session_key):
    query = (
        select(
            F1Lap.LapTime,
            F1Driver.Abbreviation,
            F1Team.TeamColor
        )
        .join(F1Lap.lap_driver)
        .join(F1Lap.lap_team)
        .where(
            F1Lap.SessionKey==session_key,
            F1Lap.PitInTime.is_(None),
            F1Lap.PitOutTime.is_(None)
        )
    )
    result = await session.execute(query)
    return result.all()


async def get_f1_race_results(session, session_key):
    query = (
        select(
            F1Driver.DriverNumber,
            F1Driver.FullName,
            F1Result.GridPosition,
            F1Result.ClassifiedPosition,
            F1Result.Time
        )
        .join(F1Result.result_driver)
        .where(F1Result.SessionKey==session_key)
    )
    result = await session.execute(query)
    return result.all()