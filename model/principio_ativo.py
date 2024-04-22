from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Principio_ativo(Base):
    __tablename__ = 'principio_ativo'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
