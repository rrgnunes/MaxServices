from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ncmcest(Base):
    __tablename__ = 'ncmcest'
    ncm = Column(VARCHAR, primary_key=True)
    cest = Column(VARCHAR, primary_key=True)
