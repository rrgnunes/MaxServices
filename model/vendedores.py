from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Vendedores(db.Model):
    __tablename__ = 'vendedores'
    codigo = Column(INTEGER, primary_key=True)
    cma = Column(DECIMAL)
    cmp = Column(DECIMAL)
    ativo = Column(VARCHAR)
    empresa = Column(INTEGER)
    flag = Column(VARCHAR)
    nome = Column(VARCHAR)
