from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nfe_fatura(Base):
    __tablename__ = 'nfe_fatura'
    codigo = Column(INTEGER, primary_key=True)
    numero = Column(VARCHAR)
    data_vencimento = Column(DATE)
    valor = Column(DECIMAL)
    fknfe = Column(INTEGER)
    fkempresa = Column(INTEGER)
