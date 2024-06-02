import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from models import Instrument, Manufacturer, Base

from models import Instrument, Manufacturer


url = URL.create(
    drivername='postgresql',
    host='localhost',
    port=5432,
    database='musicstoredb',
    username='superadmin',
    password='1234'
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()


class ValidationResponse(BaseModel):
    message: str


class ManufacturerDto(BaseModel):
    id: PositiveInt
    full_name: str


class InstrumentDto(BaseModel):
    id: PositiveInt
    name: str
    price: PositiveFloat
    manufacturer: ManufacturerDto


app = FastAPI(
    title="Music Instruments Store",
    version="1.0"
)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, port=5432)
