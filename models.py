
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer, nullable=False)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    manufacturer = relationship('Manufacturer', backref='instruments')


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    instruments = relationship('Instrument', backref='manufacturer')
