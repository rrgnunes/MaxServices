from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mesa(Base):
    __tablename__ = 'mesa'
    codigo = Column(INTEGER, primary_key=True)
    nome = Column(VARCHAR)
    qtd = Column(INTEGER)
    fk_movimento = Column(INTEGER)
    data = Column(TIMESTAMP)
    situacao = Column(VARCHAR)
    ativo = Column(VARCHAR)
