from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Grupo(db.Model):
    __tablename__ = 'grupo'
    empresa = Column(INTEGER, primary_key=True)
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    ativo = Column(VARCHAR)
