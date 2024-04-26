from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Conciliacao_lmc(db.Model):
    __tablename__ = 'conciliacao_lmc'
    codigo = Column(INTEGER, primary_key=True)
    id_fechamento = Column(INTEGER)
    tanque = Column(INTEGER)
    qtd = Column(DECIMAL)
