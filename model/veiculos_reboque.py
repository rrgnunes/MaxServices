from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Veiculos_reboque(Base):
    __tablename__ = 'veiculos_reboque'
    codigo = Column(INTEGER, primary_key=True)
    placa_cavalo = Column(VARCHAR)
    placa = Column(VARCHAR)
    municipio = Column(VARCHAR)
    uf = Column(VARCHAR)
    rntc = Column(VARCHAR)
    renavam = Column(VARCHAR)
    tipo = Column(INTEGER)
    peso = Column(DECIMAL)
    tara = Column(DECIMAL)
    carroceria = Column(SMALLINT)
