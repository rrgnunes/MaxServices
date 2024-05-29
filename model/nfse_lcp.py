from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfse_lcp(db.Model):
    __tablename__ = 'nfse_lcp'
    codigo = Column(VARCHAR, primary_key=True)
    descricao = Column(VARCHAR)
    ativo = Column(VARCHAR)