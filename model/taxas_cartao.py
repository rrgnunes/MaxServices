from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Taxas_cartao(Base):
    __tablename__ = 'taxas_cartao'
    codigo = Column(INTEGER, primary_key=True)
    parcela_1 = Column(INTEGER)
    parcela_2 = Column(INTEGER)
    taxa = Column(DECIMAL)
    fk_bandeira = Column(INTEGER)
