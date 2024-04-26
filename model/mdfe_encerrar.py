from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Mdfe_encerrar(db.Model):
    __tablename__ = 'mdfe_encerrar'
    chave = Column(VARCHAR, primary_key=True)
    protocolo = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
    situacao = Column(VARCHAR)
