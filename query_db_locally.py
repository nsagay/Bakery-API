from typing import Optional

from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlmodel import select, SQLModel, Field

CONNECTION_STRING = ('Driver={SQL Server};'
                     'Server=LONNB22396'
                     'Database=Bakery;'
                     'Trusted_Connection=True;'
                     )

CONNECTION_URL = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": CONNECTION_STRING}
)

engine = create_engine(CONNECTION_URL, pool_size=500, max_overflow=0, echo=True, future=True)
session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


#  Use this if you want to create a session not connected to a web request, e.g. for manual testing of solutions:
def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


engine = create_engine(CONNECTION_URL)
session = next(get_db())


class Sweet(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    item_name: Optional[str]
    price: Optional[float]


def get_sweets():
    table = Sweet
    statement = select(table)
    results = session.execute(statement).all()
    return results


print(get_sweets())
