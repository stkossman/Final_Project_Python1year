import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, PositiveInt, PositiveFloat
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker
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
    version="1.0",
    description="<h2>Music Instruments Store Database.</h2> <h3>Made by stkossman</h3>"
)


@app.get("/instruments", response_model=list[InstrumentDto])
def get_instruments():
    db = next(get_db())
    instruments = db.query(Instrument).all()
    return instruments


@app.get("/instruments/{instrument_id}", response_model=InstrumentDto)
def get_one_instrument(instrument_id: int):
    db = next(get_db())
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@app.get("/manufacturers", response_model=list[ManufacturerDto])
def get_manufacturers():
    db = next(get_db())
    manufacturers = db.query(Manufacturer).all()
    return manufacturers


@app.get("/manufacturers/{manufacturer_id}", response_model=ManufacturerDto)
def get_one_manufacturer(manufacturer_id: int):
    db = next(get_db())
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer


@app.post("/instruments", response_model=InstrumentDto)
def create_instrument(instrument: InstrumentDto):
    db = next(get_db())
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == instrument.manufacturer.id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    new_instrument = Instrument(
        name=instrument.name, price=instrument.price, manufacturer_id=instrument.manufacturer.id)
    db.add(new_instrument)
    db.commit()
    db.refresh(new_instrument)
    return new_instrument


@app.post("/manufacturers", response_model=ManufacturerDto)
def create_manufacturer(manufacturer: ManufacturerDto):
    db = next(get_db())
    new_manufacturer = Manufacturer(full_name=manufacturer.full_name)
    db.add(new_manufacturer)
    db.commit()
    db.refresh(new_manufacturer)
    return new_manufacturer


@app.put("/instruments", response_model=InstrumentDto)
def update_instrument(instrument_id: int, name: str, price: float):
    db = next(get_db())
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    instrument.name = name
    instrument.price = price
    db.commit()
    db.refresh(instrument)
    return instrument


@app.put("/manufacturers", response_model=ManufacturerDto)
def update_manufacturer(manufacturer_id: int, full_name: str):
    db = next(get_db())
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    manufacturer.full_name = full_name
    db.commit()
    db.refresh(manufacturer)
    return manufacturer


@app.delete("/instruments")
def delete_instrument(instrument_id: int):
    db = next(get_db())
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    db.delete(instrument)
    db.commit()
    return ValidationResponse(message="Instrument deleted")


@app.delete("/manufacturers")
def delete_manufacturer(manufacturer_id: int):
    db = next(get_db())
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    db.delete(manufacturer)
    db.commit()
    return ValidationResponse(message="Manufacturer deleted")


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, port=5432)
