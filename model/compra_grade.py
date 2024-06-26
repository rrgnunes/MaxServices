from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Compra_grade(db.Model):
    __tablename__ = 'compra_grade'
    codigo = Column(INTEGER, primary_key=True)
    fk_itens_compra = Column(INTEGER)
    fk_produto = Column(INTEGER)
    descricao = Column(VARCHAR)
    qtd = Column(DECIMAL)
