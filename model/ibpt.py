from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ibpt(Base):
    __tablename__ = 'ibpt'
    codigo = Column(VARCHAR, primary_key=True)
    ex = Column(VARCHAR)
    tipo = Column(VARCHAR)
    descricao = Column(VARCHAR)
    nacionalfederal = Column(VARCHAR)
    importadosfederal = Column(VARCHAR)
    estadual = Column(VARCHAR)
    municipal = Column(VARCHAR)
    vigenciainicio = Column(VARCHAR)
    vigenciafim = Column(VARCHAR)
    chave = Column(VARCHAR)
    fonte = Column(VARCHAR)
    versao = Column(VARCHAR, primary_key=True)
