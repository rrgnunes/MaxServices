from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vendas_bico(Base):
    __tablename__ = 'vendas_bico'
    codigo = Column(INTEGER, primary_key=True)
    id_venda = Column(INTEGER)
    id_bico = Column(INTEGER)
    valor = Column(DECIMAL)
    qtd = Column(DECIMAL)
    total = Column(DECIMAL)
    datac_emissao = Column(DATE)
    id_produto = Column(INTEGER)
