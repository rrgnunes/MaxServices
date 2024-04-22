from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Operadora_cartao(Base):
    __tablename__ = 'operadora_cartao'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    contadestino = Column(VARCHAR)
    data_cad = Column(DATE)
    empresa = Column(INTEGER)
