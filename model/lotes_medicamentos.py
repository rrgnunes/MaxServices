from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Lotes_medicamentos(db.Model):
    __tablename__ = 'lotes_medicamentos'
    codigo = Column(INTEGER, primary_key=True)
    fk_nfe = Column(INTEGER)
    fk_produto = Column(INTEGER)
    n_lote = Column(VARCHAR)
    data_fabricao = Column(TIMESTAMP)
    data_validade = Column(TIMESTAMP)
