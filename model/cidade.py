from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cidade(db.Model):
    __tablename__ = 'cidade'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    coduf = Column(INTEGER)
    uf = Column(VARCHAR)
