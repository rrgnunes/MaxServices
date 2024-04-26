from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Produto_composicao(db.Model):
    __tablename__ = 'produto_composicao'
    fk_produto = Column(INTEGER, primary_key=True)
    id_produto = Column(INTEGER, primary_key=True)
    quantidade = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
