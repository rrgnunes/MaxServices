from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Orcamento_item(db.Model):
    __tablename__ = 'orcamento_item'
    codigo = Column(INTEGER, primary_key=True)
    fk_orcamento = Column(INTEGER)
    fk_produto = Column(INTEGER)
    qtd = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
    item = Column(SMALLINT)
    fk_grade = Column(INTEGER)
