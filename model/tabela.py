from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Tabela(db.Model):
    __tablename__ = 'tabela'
    codigo = Column(INTEGER, primary_key=True)
    ordem = Column(INTEGER)
    tabela = Column(VARCHAR)
    envia = Column(VARCHAR)
    recebe = Column(VARCHAR)
    fk_servidor = Column(INTEGER)
