from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Vendas_composicao(db.Model):
    __tablename__ = 'vendas_composicao'
    codigo = Column(INTEGER, primary_key=True)
    fk_venda_detalhe = Column(INTEGER)
    id_produto = Column(INTEGER)
    qtd = Column(DECIMAL)
    qtd_devolvida = Column(DECIMAL)
