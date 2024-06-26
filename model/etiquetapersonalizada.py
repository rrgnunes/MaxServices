from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Etiquetapersonalizada(db.Model):
    __tablename__ = 'etiquetapersonalizada'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    etiqueta = Column(VARCHAR)
    comando = Column(VARCHAR)
    tipo = Column(SMALLINT)
