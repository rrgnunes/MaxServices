from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Paises(db.Model):
    __tablename__ = 'paises'
    codigo = Column(INTEGER, primary_key=True)
    nome = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
