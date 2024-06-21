from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, PositiveInt, PositiveFloat
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from models import Manufacturer, Instrument


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


class ValidationResponse(BaseModel):
    message: str


class InstrumentDto(BaseModel):
    id: Optional[PositiveInt]
    name: str
    price: PositiveFloat
    manufacturer_id: int


class ManufacturerDto(BaseModel):
    id: Optional[PositiveInt]
    full_name: str


class ManufacturerInfo(BaseModel):
    id: PositiveInt
    full_name: str
    instruments: list[InstrumentDto]


mapping = {'a': 'ф', 'b': 'і', 'c': 'с', 'd': 'в', 'e': 'у', 'f': 'а', 'g': 'п', 'h': 'р', 'i': 'ш', 'j': 'о', 'k': 'л',
            'l': 'д', 'm': 'ь', 'n': 'т', 'o': 'щ', 'p': 'з', 'q': 'й', 'r': 'к', 's': 'і', 't': 'е', 'u': 'г', 'v': 'м',
            'w': 'ц', 'x': 'ч', 'y': 'н', 'z': 'я',
    'A': 'Ф', 'B': 'І', 'C': 'С', 'D': 'В', 'E': 'У', 'F': 'А', 'G': 'П', 'H': 'Р', 'I': 'Ш', 'J': 'О', 'K': 'Л', 'L': 'Д',
            'M': 'Ь', 'N': 'Т', 'O': 'Щ', 'P': 'З', 'Q': 'Й', 'R': 'К', 'S': 'І', 'T': 'Е', 'U': 'Г', 'V': 'М', 'W': 'Ц',
            'X': 'Ч', 'Y': 'Н', 'Z': 'Я'}

reverse_mapping = {v: k for k, v in mapping.items()}


def translate_to_english(text):
    translated_text = ""
    for char in text:
        if char in reverse_mapping:
            translated_text += reverse_mapping[char]
        else:
            translated_text += char
    return translated_text


class StoreManager:
    def __init__(self):
        self.session = Session()

    def get_instruments(self):
        instruments = self.session.query(Instrument).all()
        return instruments

    def get_one_instrument(self, instrument_id: int):
        instrument = self.session.query(Instrument).filter(Instrument.id == instrument_id).first()
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")
        return instrument

    def get_manufacturers(self):
        manufacturers = self.session.query(Manufacturer).all()
        return manufacturers

    def get_one_manufacturer(self, manufacturer_id: int):
        manufacturer = self.session.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
        if manufacturer is None:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        instruments = self.session.query(Instrument).filter(Instrument.manufacturer_id == manufacturer_id).all()
        man_with_instruments = {"id": manufacturer.id, "full_name": manufacturer.full_name, "instruments": instruments}
        return man_with_instruments

    def create_instrument(self, instrument: InstrumentDto):
        manufacturer = self.session.query(Manufacturer).filter(Manufacturer.id == instrument.manufacturer_id).first()
        if manufacturer is None:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        new_instrument = Instrument(
            name=instrument.name,
            price=instrument.price,
            manufacturer_id=instrument.manufacturer_id
        )
        self.session.add(new_instrument)
        self.session.commit()
        self.session.refresh(new_instrument)
        return new_instrument

    def create_manufacturer(self, manufacturer: ManufacturerDto):
        new_manufacturer = Manufacturer(full_name=manufacturer.full_name)
        self.session.add(new_manufacturer)
        self.session.commit()
        self.session.refresh(new_manufacturer)
        return new_manufacturer

    def update_instrument(self, instrument_id: PositiveInt, name: str, price: PositiveFloat):
        instrument = self.session.query(Instrument).filter(Instrument.id == instrument_id).first()
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")
        instrument.name = name
        instrument.price = price
        self.session.commit()
        self.session.refresh(instrument)
        return instrument

    def update_manufacturer(self, manufacturer_id: PositiveInt, full_name: str):
        manufacturer = self.session.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
        if manufacturer is None:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        manufacturer.full_name = full_name
        self.session.commit()
        self.session.refresh(manufacturer)
        return manufacturer

    def delete_instrument(self, instrument_id: PositiveInt):
        instrument = self.session.query(Instrument).filter(Instrument.id == instrument_id).first()
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")
        self.session.delete(instrument)
        self.session.commit()
        return ValidationResponse(message="Instrument deleted")

    def delete_manufacturer(self, manufacturer_id: PositiveInt):
        manufacturer = self.session.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
        if manufacturer is None:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        self.session.delete(manufacturer)
        self.session.commit()
        return ValidationResponse(message="Manufacturer deleted")

    def search_instruments(self, query: str):
        translated = translate_to_english(query)
        instruments = self.session.query(Instrument).filter(Instrument.name.like(f'%{translated}%')).all()
        return instruments

    def delete_all_instruments(self):
        instruments = self.session.query(Instrument).all()

        for instrument in instruments:
            self.session.delete(instrument)

        self.session.commit()
        sql_statement = text(f"ALTER SEQUENCE {Instrument.__table__.name}_id_seq RESTART WITH 1")
        self.session.execute(sql_statement)
        self.session.commit()

    def delete_all_manufacturers(self):
        manufacturers = self.session.query(Manufacturer).all()

        for manufacturer in manufacturers:
            self.session.delete(manufacturer)

        self.session.commit()
        sql_statement = text(f"ALTER SEQUENCE {Manufacturer.__table__.name}_id_seq RESTART WITH 1")
        self.session.execute(sql_statement)
        self.session.commit()


app = FastAPI(
    title="Music Instruments Store",
    version="1.0",
    description="<h2>Music Instruments Store Database.</h2> <h3>Made by stkossman</h3>"
)

stmanager = StoreManager()


@app.get("/instruments", response_model=list[InstrumentDto])
def get_instruments():
    instruments = stmanager.get_instruments()
    return instruments


@app.get("/instruments/{instrument_id}", response_model=InstrumentDto)
def get_one_instrument(instrument_id: int):
    instrument = stmanager.get_one_instrument(instrument_id)
    return instrument


@app.get("/manufacturers", response_model=list[ManufacturerDto])
def get_manufacturers():
    manufacturers = stmanager.get_manufacturers()
    return manufacturers


@app.get("/manufacturers/{manufacturer_id}", response_model=ManufacturerInfo)
def get_one_manufacturer(manufacturer_id: int):
    manufacturer = stmanager.get_one_manufacturer(manufacturer_id)
    return manufacturer


@app.post("/instruments", response_model=InstrumentDto)
def create_instrument(instrument: InstrumentDto):
    new_instrument = stmanager.create_instrument(instrument)
    return new_instrument


@app.post("/manufacturers", response_model=ManufacturerDto)
def create_manufacturer(manufacturer: ManufacturerDto):
    new_manufacturer = stmanager.create_manufacturer(manufacturer)
    return new_manufacturer


@app.put("/instruments", response_model=InstrumentDto)
def update_instrument(instrument_id: int, name: str, price: float):
    updated_instrument = stmanager.update_instrument(instrument_id, name, price)
    return updated_instrument


@app.put("/manufacturers", response_model=ManufacturerDto)
def update_manufacturer(manufacturer_id: int, full_name: str):
    updated_manufacturer = stmanager.update_manufacturer(manufacturer_id, full_name)
    return updated_manufacturer


@app.delete("/instruments")
def delete_instrument(instrument_id: int):
    res = stmanager.delete_instrument(instrument_id)
    return res


@app.delete("/manufacturers")
def delete_manufacturer(manufacturer_id: int):
    res = stmanager.delete_manufacturer(manufacturer_id)
    return res


@app.get("/instruments/search/", response_model=list[InstrumentDto])
def search_instruments(query: str = Query(..., min_length=1)):
    instruments = stmanager.search_instruments(query)
    return instruments


@app.delete("/instruments/")
def delete_all_instruments():
    res = stmanager.delete_all_instruments()
    return res


@app.delete("/manufacturers/")
def delete_all_manufacturers():
    res = stmanager.delete_all_manufacturers()
    return res


if __name__ == "__main__":
    uvicorn.run(app, port=5432)
