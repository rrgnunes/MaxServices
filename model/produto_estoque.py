from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Produto_estoque(Base):
    __tablename__ = 'produto_estoque'
    produto = Column(INTEGER, primary_key=True)
    empresa = Column(INTEGER, primary_key=True)
    estoque_atual = Column(NUMERIC)
