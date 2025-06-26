from utils.config import DRIVER_NAME, USERNAME, PASSWORD, HOST, PORT, DATABASE
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

url = URL.create(drivername=DRIVER_NAME,
                 username=USERNAME,
                 password=PASSWORD,
                 host=HOST,
                 port=PORT,
                 database=DATABASE)

engine = create_async_engine(url, echo=False)  # , connect_args={"client_encoding": "utf8"}

async_session = sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    class_=AsyncSession
)