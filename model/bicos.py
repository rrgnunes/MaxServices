from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Bicos(db.Model):
    __tablename__ = 'bicos'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    tipo = Column(INTEGER)
    id_bomba = Column(INTEGER)
    qtd = Column(DECIMAL)
