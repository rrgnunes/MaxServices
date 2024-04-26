from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Unidade(db.Model):
    __tablename__ = 'unidade'
    codigo = Column(VARCHAR, primary_key=True)
    descricao = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
