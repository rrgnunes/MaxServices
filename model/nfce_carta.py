from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfce_carta(db.Model):
    __tablename__ = 'nfce_carta'
    codigo = Column(INTEGER, primary_key=True)
    fk_nfce = Column(INTEGER)
    sequencia = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    data = Column(DATE)
    correcao = Column(BLOB)
