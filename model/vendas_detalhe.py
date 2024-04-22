from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vendas_detalhe(Base):
    __tablename__ = 'vendas_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fkvenda = Column(INTEGER)
    id_produto = Column(INTEGER)
    item = Column(SMALLINT)
    cod_barra = Column(VARCHAR)
    qtd = Column(DECIMAL)
    e_medio = Column(DECIMAL)
    preco = Column(DECIMAL)
    valor_item = Column(DECIMAL)
    vdesconto = Column(DECIMAL)
    total = Column(DECIMAL)
    situacao = Column(VARCHAR)
    unidade = Column(VARCHAR)
    qtd_devolvida = Column(DECIMAL)
    acrescimo = Column(DECIMAL)
    os = Column(VARCHAR)
    fk_grade = Column(INTEGER)
