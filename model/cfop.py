from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cfop(Base):
    __tablename__ = 'cfop'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    tipo = Column(VARCHAR)
    mov_es = Column(VARCHAR)
    operacao = Column(VARCHAR)
    ativo = Column(VARCHAR)
