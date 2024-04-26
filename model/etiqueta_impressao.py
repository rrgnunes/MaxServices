from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Etiqueta_impressao(db.Model):
    __tablename__ = 'etiqueta_impressao'
    codigo = Column(INTEGER, primary_key=True)
    fk_produto = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    qtd = Column(INTEGER)
