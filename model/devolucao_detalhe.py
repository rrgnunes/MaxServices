from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Devolucao_detalhe(db.Model):
    __tablename__ = 'devolucao_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fk_devolucao = Column(INTEGER)
    fk_produto = Column(INTEGER)
    qtd = Column(DECIMAL)
    qtd_vendida = Column(DECIMAL)
    preco = Column(DECIMAL)
    fk_devolucao_item = Column(INTEGER)
    item = Column(INTEGER)
    total = Column(DECIMAL)
