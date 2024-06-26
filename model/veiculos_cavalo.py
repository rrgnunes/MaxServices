from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Veiculos_cavalo(db.Model):
    __tablename__ = 'veiculos_cavalo'
    placa = Column(VARCHAR, primary_key=True)
    descricao = Column(VARCHAR)
    municipio = Column(VARCHAR)
    uf = Column(VARCHAR)
    renavam = Column(VARCHAR)
    rntc = Column(VARCHAR)
    tipo = Column(INTEGER)
    tara = Column(DECIMAL)
    peso = Column(DECIMAL)
    ativo = Column(VARCHAR)
    carroceria = Column(INTEGER)
