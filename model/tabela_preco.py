from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Tabela_preco(db.Model):
    __tablename__ = 'tabela_preco'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    acrescimo = Column(DECIMAL)
    fkempresa = Column(INTEGER)
    ativo = Column(VARCHAR)
