from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Lmc(db.Model):
    __tablename__ = 'lmc'
    codigo = Column(INTEGER, primary_key=True)
    id_empresa = Column(INTEGER)
    datacad = Column(DATE)
    id_produto = Column(INTEGER)
    p_avista = Column(DECIMAL)
    p_prazo = Column(DECIMAL)
    totalabertura = Column(DECIMAL)
    totalsaida = Column(DECIMAL)
    observacoes = Column(VARCHAR)
    id_tanque = Column(INTEGER)
