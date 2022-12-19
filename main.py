from typing import Optional

from fastapi import FastAPI, Depends
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session
from sqlmodel import select, SQLModel, Field

app = FastAPI()

CONNECTION_STRING = ('Driver={SQL Server};'
                     'Server=LONNB22396;'
                     'Database=Bakery;'
                     'Trusted_Connection=True;'
                     )

CONNECTION_URL = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": CONNECTION_STRING}
)

engine = create_engine(CONNECTION_URL, pool_size=500, max_overflow=0, echo=True, future=True)
session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
ScopedSession = scoped_session(session_factory)


#  Use this when creating a scoped session, i.e. a session linked to a web request:
async def get_session() -> Session:
    try:
        session = ScopedSession()
        return session
    finally:
        # session.remove()  #  this is the way that SQLAlchemy suggests a ScopedSession should be closed like
        session.close()  # this is the way that Ki closes their session


class Sweet(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    item_name: Optional[str]
    price: Optional[float]

def create_tables():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def hello_world():
    return {"My message to the World": "Hello World!"}

@app.get("/{name}")
def hello_world_with_path_parameter(name: str):
    return {f"My message to {name}": f"Hello {name}!"}
    
@app.get("/create_table/")
def lol():
    create_tables()
    return {"Table created": "true"}




@app.get("/sweet/")
async def get_all_sweets(session: Session = Depends(get_session)):
     table = Sweet
     statement = select(table)
     results = session.execute(statement).all()
     return results


@app.get("/sweet/{item_name}")
async def query_sweets(item_name: str, session: Session = Depends(get_session)):
    table = Sweet
    statement = select(table).where(table.item_name == item_name)
    results = session.execute(statement).all()
    if not results:
        return {"results": "No luck mate"}
    else:
         return {"results": results}

@app.get("/price/{item_name}")
async def price_sweet(item_name: str, session: Session = Depends(get_session)):
    table = Sweet
    statement = select(table.price).where(table.item_name == item_name)
    results = session.execute(statement).all()
    if not results:
        return {"results": "No luck mate"}
    else:
         return {"results": results}

@app.get("/price/")
async def sum_sweets(session: Session = Depends(get_session)):
    table = Sweet
    statement = select(table.price)
    results = session.execute(statement).all()
    if not results:
        return {"results": "No luck mate"}
    else:
         return  {"results": results}

@app.post("/add/")
async def create_sweet(obj_: Sweet, session: Session = Depends(get_session)):
    sweet_1 = Sweet(item_name = obj_.item_name, price = obj_.price)
    session.add(sweet_1)  
    session.commit()
    return {"results": "lol"}
    