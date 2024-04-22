from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recibo(Base):
    __tablename__ = 'recibo'
    codigo = Column(INTEGER, primary_key=True)
    fkempresa = Column(INTEGER)
    data_emissao = Column(DATE)
    valor = Column(DECIMAL)
    nominal = Column(VARCHAR)
    referente1 = Column(VARCHAR)
    referente2 = Column(VARCHAR)
    situacao = Column(VARCHAR)
