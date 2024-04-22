from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Comanda_rateio(Base):
    __tablename__ = 'comanda_rateio'
    codigo = Column(INTEGER, primary_key=True)
    fk_comanda_pessoa = Column(INTEGER)
    fk_comanda = Column(INTEGER)
    fk_produto = Column(INTEGER)
    percentual = Column(DECIMAL)
    qtd = Column(DECIMAL)
    total = Column(DECIMAL)
    preco = Column(DECIMAL)
