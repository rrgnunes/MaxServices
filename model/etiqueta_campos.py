from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Etiqueta_campos(db.Model):
    __tablename__ = 'etiqueta_campos'
    codigo = Column(INTEGER, primary_key=True)
    campo = Column(VARCHAR)
    coluna = Column(INTEGER)
    linha = Column(INTEGER)
    fontes = Column(INTEGER)
    visivel = Column(VARCHAR)
    fk_etiquetas = Column(INTEGER)
    caracteres = Column(INTEGER)
    descricao = Column(VARCHAR)
