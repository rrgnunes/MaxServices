from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfe_carta(db.Model):
    __tablename__ = 'nfe_carta'
    codigo = Column(INTEGER, primary_key=True)
    fk_nfe = Column(INTEGER)
    sequencia = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    data = Column(DATE)
    correcao = Column(BLOB)
    fk_usuario = Column(INTEGER)
