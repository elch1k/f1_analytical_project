from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, SmallInteger, String, Integer, Boolean, Numeric, DateTime, TIMESTAMP, TIME
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from datetime import datetime


class Base(DeclarativeBase):
    pass


class F1Event(Base):
    __tablename__ = 'f1_event'

    MeetingKey: Mapped[int] = mapped_column(primary_key=True)
    SessionKey: Mapped[int] = mapped_column(primary_key=True)

    Season: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    WeekendNumber: Mapped[int | None] = mapped_column(SmallInteger, nullable=False)
    ShortName: Mapped[str] = mapped_column(String(80), nullable=False)
    FullName: Mapped[str | None] = mapped_column(String(120), nullable=True)
    CountryName: Mapped[str | None] = mapped_column(String(100), nullable=True)
    LocationType: Mapped[str | None] = mapped_column(String(120), nullable=True)
    CircuitName: Mapped[str | None] = mapped_column(String(150), nullable=True)
    SessionType: Mapped[str] = mapped_column(String(40), nullable=False)
    SessionName: Mapped[str] = mapped_column(String(40), nullable=False)
    LocalStartDate: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=False))
    LocalEndDate: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=False))
    GMTStartDate: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=False))
    GMTEndDate: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=False))

    # __table_args__= (
    #     PrimaryKeyConstraint('MeetingKey', 'SessionKey'),
    # )
    weathers = relationship("F1Weather", backref="event")
    results = relationship("F1Result", backref="event")
    controls = relationship("F1FIAControl", backref="event")
    laps = relationship("F1Lap", backref="event")
    telemeties = relationship("F1Telemetry", backref="event")
    # event_weather: Mapped[list["F1Weather"]] = relationship(
    #     back_populates="weather_event",
    #     foreign_keys=["F1Weather.MeetingKey", "F1Weather.SessionKey"]
    #     )

    # event_result: Mapped[list["F1Result"]] = relationship(
    #     back_populates="result_event",
    #     foreign_keys=["F1Result.MeetingKey", "F1Result.SessionKey"]
    # )
    # event_fia_control: Mapped[list["F1FIAControl"]] = relationship(
    #     back_populates="fia_control_event",
    #     foreign_keys=["F1FIAControl.MeetingKey", "F1FIAControl.SessionKey"]
    # )
    # event_lap: Mapped[list["F1Lap"]] = relationship(
    #     back_populates="lap_event",
    #     foreign_keys=["F1Lap.MeetingKey", "F1Lap.SessionKey"]
    # )
    # event_telemetry: Mapped[list["F1Telemetry"]] = relationship(
    #     back_populates="telemetry_event",
    #     foreign_keys=["F1Telemetry.MeetingKey", "F1Telemetry.SessionKey"]
    # )


class F1Weather(Base):
    __tablename__ = "f1_weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MeetingKey: Mapped[int] = mapped_column(nullable=False)  # ForeignKey("f1_event.MeetingKey"),
    SessionKey: Mapped[int] = mapped_column(nullable=False)  # ForeignKey("f1_event.SessionKey"), 
    Time: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    AirTemp: Mapped[float] = mapped_column(Numeric, nullable=True)
    Humidity: Mapped[float] = mapped_column(Numeric, nullable=True)
    Pressure: Mapped[float] = mapped_column(Numeric, nullable=True)
    Rainfall: Mapped[bool] = mapped_column(Boolean, nullable=True)
    TrackTemp: Mapped[float] = mapped_column(Numeric, nullable=True)
    WindDirection: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    WindSpeed: Mapped[float] = mapped_column(Numeric, nullable=True)

    # if we are using composite primary key we should explicitly point it, not in mapped_column
    # also each class model should contain at least one primary key column
    __table_args__ = (
        ForeignKeyConstraint(
            [MeetingKey, SessionKey],
            [F1Event.MeetingKey, F1Event.SessionKey],
            name='FK_weather_event'
        ),
    )

    # weather_event: Mapped["F1Event"] = relationship(
    #     back_populates="event_weather",
    #     foreign_keys=[MeetingKey, SessionKey]
    # )


class F1Driver(Base):
    __tablename__ = "f1_driver"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    Abbreviation: Mapped[str] = mapped_column(String(10), nullable=True)
    FullName: Mapped[str] = mapped_column(String(80), nullable=True)
    DriverNumber: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    CountryCode: Mapped[str] = mapped_column(String(5), nullable=True)
    HeadshotUrl: Mapped[str] = mapped_column(String(180), nullable=True)

    driver_result: Mapped[list["F1Result"]] = relationship(back_populates="result_driver")
    driver_fia_control: Mapped[list["F1FIAControl"]] = relationship(back_populates="fia_control_driver")
    driver_lap: Mapped[list["F1Lap"]] = relationship(back_populates="lap_driver")
    driver_telemetry: Mapped[list["F1Telemetry"]] = relationship(back_populates="telemetry_driver")


class F1Team(Base):
    __tablename__ = "f1_team"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    TeamName: Mapped[str] = mapped_column(String(60), nullable=True)
    TeamColor: Mapped[str] = mapped_column(String(10), nullable=True)

    team_result: Mapped[list["F1Result"]] = relationship(back_populates="result_team")
    team_lap: Mapped[list["F1Lap"]] = relationship(back_populates="lap_team")


class F1Result(Base):
    __tablename__ = "f1_result"

    MeetingKey: Mapped[int] = mapped_column(primary_key=True) # ForeignKey("f1_event.MeetingKey"), 
    SessionKey: Mapped[int] = mapped_column(primary_key=True)  # ForeignKey("f1_event.SessionKey"), 
    DriverId: Mapped[int] = mapped_column(ForeignKey("f1_driver.id"), primary_key=True)
    TeamId: Mapped[int] = mapped_column(ForeignKey("f1_team.id"), primary_key=True)
    Position: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ClassifiedPosition: Mapped[str | None] = mapped_column(String(5), nullable=True)
    GridPosition: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    Q1: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False), nullable=True)
    Q2: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False), nullable=True)
    Q3: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False), nullable=True)
    Time: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False), nullable=True)
    Status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    Points: Mapped[float | None] = mapped_column(Numeric, nullable=True)

    # __table_args__=(
    #     PrimaryKeyConstraint('MeetingKey', 'SessionKey', 'DriverId', 'TeamId'),
    # )

    __table_args__ = (
        ForeignKeyConstraint(
            [MeetingKey, SessionKey],
            [F1Event.MeetingKey, F1Event.SessionKey],
            name='FK_result_event'
        ),
    )

    # result_event: Mapped["F1Event"] = relationship(
    #     back_populates="event_result",
    #     foreign_keys=[MeetingKey, SessionKey]
    # )
    result_driver: Mapped["F1Driver"] = relationship(
        back_populates="driver_result"
        )
    result_team: Mapped["F1Team"] = relationship(
        back_populates="team_result"
        )


class F1FIAControl(Base):
    __tablename__ = "f1_fia_control"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MeetingKey: Mapped[int] = mapped_column(nullable=False)
    SessionKey: Mapped[int] = mapped_column(nullable=False) 
    DriverId: Mapped[int | None] = mapped_column(ForeignKey("f1_driver.id"))
    Time: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    Lap: Mapped[int | None] = mapped_column(SmallInteger)
    Category: Mapped[str] = mapped_column(String(20), nullable=True)
    Message: Mapped[str] = mapped_column(String(255), nullable=True)
    Status: Mapped[str | None] = mapped_column(String(40))
    Flag: Mapped[str | None] = mapped_column(String(20))
    Scope: Mapped[str | None] = mapped_column(String(10))
    Sector: Mapped[int | None] = mapped_column(SmallInteger)

    __table_args__ = (
        ForeignKeyConstraint(
            [MeetingKey, SessionKey],
            [F1Event.MeetingKey, F1Event.SessionKey],
            name="FK_fia_control_event"
        ),
    )

    # fia_control_event: Mapped["F1Event"] = relationship(
    #     back_populates="event_fia_control",
    #     foreign_keys=[MeetingKey, SessionKey]
    # )
    fia_control_driver: Mapped["F1Driver"] = relationship(back_populates="driver_fia_control")


class F1Lap(Base):
    __tablename__ = "f1_lap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MeetingKey: Mapped[int] = mapped_column(nullable=False)
    SessionKey: Mapped[int] = mapped_column(nullable=False)
    DriverId: Mapped[int] = mapped_column(ForeignKey("f1_driver.id"))
    TeamId: Mapped[int] = mapped_column(ForeignKey("f1_team.id"))
    Time: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    LapTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    LapNumber: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    Stint: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    PitOutTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    PitInTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector1Time: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector2Time: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector3Time: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector1SessionTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector2SessionTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    Sector3SessionTime: Mapped[datetime | None] = mapped_column(type_=TIME(timezone=False))
    SpeedI1: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    SpeedI2: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    SpeedFL: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    SpeedST: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    IsPersonalBest: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    Compound: Mapped[str] = mapped_column(String(20), nullable=True)
    TyreLife: Mapped[int] = mapped_column(Integer, nullable=True)
    FreshTyre: Mapped[bool] = mapped_column(Boolean, nullable=True)
    LapStartTime: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    LapStartDate: Mapped[datetime | None] = mapped_column(type_=TIMESTAMP(timezone=False))
    TrackStatus: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    Position: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    Deleted: Mapped[bool] = mapped_column(Boolean, nullable=True)
    DeletedReason: Mapped[str | None] = mapped_column(String(60), nullable=True)
    FastF1Generated: Mapped[bool] = mapped_column(Boolean, nullable=True)
    IsAccurate: Mapped[bool] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            [MeetingKey, SessionKey],
            [F1Event.MeetingKey, F1Event.SessionKey],
            name='FK_lap_event'
        ),
    )

    # lap_event: Mapped["F1Event"] = relationship(
    #     back_populates="event_lap",
    #     foreign_keys=[MeetingKey, SessionKey]
    # )
    lap_driver: Mapped["F1Driver"] = relationship(back_populates="driver_lap")
    lap_team: Mapped["F1Team"] = relationship(back_populates="team_lap")


class F1Telemetry(Base):
    __tablename__ = "f1_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MeetingKey: Mapped[int] = mapped_column(nullable=False)  # ForeignKey("f1_event.MeetingKey"),
    SessionKey: Mapped[int] = mapped_column(nullable=False)  # ForeignKey("f1_event.SessionKey"),
    DriverId: Mapped[int] = mapped_column(ForeignKey("f1_driver.id"))
    Date: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=False))
    RPM: Mapped[float] = mapped_column(Numeric, nullable=True)
    Speed: Mapped[float] = mapped_column(Numeric, nullable=True)
    nGear: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    Throttle: Mapped[float] = mapped_column(Numeric, nullable=True)
    Brake: Mapped[bool] = mapped_column(Boolean, nullable=True)
    DRS: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    Time: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    SessionTime: Mapped[datetime] = mapped_column(type_=TIME(timezone=False))
    Distance: Mapped[float] = mapped_column(Numeric, nullable=True)
    LapNumber: Mapped[int] = mapped_column(SmallInteger, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            [MeetingKey, SessionKey],
            [F1Event.MeetingKey, F1Event.SessionKey],
            name='FK_telemetry_event'
        ),
    )

    # telemetry_event: Mapped["F1Event"] = relationship(
    #     back_populates="event_telemetry",
    #     foreign_keys=[MeetingKey, SessionKey]
    # )
    telemetry_driver: Mapped["F1Driver"] = relationship(back_populates="driver_telemetry")