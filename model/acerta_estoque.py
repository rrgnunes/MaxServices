from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Acerta_estoque(db.Model):
    __tablename__ = 'acerta_estoque'
    codigo = Column(INTEGER, primary_key=True)
    fkproduto = Column(INTEGER)
    data = Column(DATE)
    e_s = Column(VARCHAR)
    qtd_f = Column(DECIMAL)
    qtd_a = Column(DECIMAL)
    fk_empresa = Column(INTEGER)
