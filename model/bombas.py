from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bombas(Base):
    __tablename__ = 'bombas'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    id_tanque = Column(INTEGER)
    serie = Column(INTEGER)
    fabricante = Column(VARCHAR)
    modelo = Column(VARCHAR)
    tipo_medicao = Column(INTEGER)
    num_lacre = Column(INTEGER)
    dt_aplicacao = Column(DATE)
