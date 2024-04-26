from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Contas(db.Model):
    __tablename__ = 'contas'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    tipo = Column(VARCHAR)
    data_abertura = Column(DATE)
    id_usuario = Column(INTEGER)
    empresa = Column(INTEGER)
    lote = Column(INTEGER)
    situacao = Column(VARCHAR)
