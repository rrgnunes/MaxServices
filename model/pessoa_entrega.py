from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Pessoa_entrega(db.Model):
    __tablename__ = 'pessoa_entrega'
    fkcliente = Column(INTEGER, primary_key=True)
    endereco = Column(VARCHAR)
    complemento = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cidade = Column(VARCHAR)
    uf = Column(VARCHAR)
    cep = Column(VARCHAR)
    fone = Column(VARCHAR)
