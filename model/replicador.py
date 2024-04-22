from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Replicador(Base):
    __tablename__ = 'replicador'
    tabela = Column(VARCHAR)
    acao = Column(VARCHAR)
    chave = Column(VARCHAR)
    codigo = Column(BIGINT, primary_key=True)
