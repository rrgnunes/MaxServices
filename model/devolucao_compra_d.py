from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Devolucao_compra_d(Base):
    __tablename__ = 'devolucao_compra_d'
    codigo = Column(INTEGER, primary_key=True)
    fk_devolucao_compra_m = Column(INTEGER)
    id_produto = Column(INTEGER)
    qtd_comprada = Column(DECIMAL)
    qtd_devolvida = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
    fk_compra_item = Column(INTEGER)
