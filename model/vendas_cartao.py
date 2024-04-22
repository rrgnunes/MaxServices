from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vendas_cartao(Base):
    __tablename__ = 'vendas_cartao'
    codigo = Column(INTEGER, primary_key=True)
    fk_venda = Column(INTEGER, primary_key=True)
    data_emissao = Column(DATE)
    fk_taxas_cartao = Column(INTEGER)
    total_cartao = Column(DECIMAL)
    total_venda = Column(DECIMAL)
