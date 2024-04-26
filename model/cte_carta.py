from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cte_carta(db.Model):
    __tablename__ = 'cte_carta'
    codigo = Column(INTEGER, primary_key=True)
    fk_cte = Column(INTEGER)
    sequencia = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    data = Column(DATE)
    correcao = Column(BLOB)
