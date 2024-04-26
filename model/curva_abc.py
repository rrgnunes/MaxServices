from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Curva_abc(db.Model):
    __tablename__ = 'curva_abc'
    id_produto = Column(INTEGER, primary_key=True)
    qtd = Column(DECIMAL)
    total = Column(DECIMAL)
    percentual = Column(DECIMAL)
    curva = Column(VARCHAR)
    fkempresa = Column(INTEGER)
