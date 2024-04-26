from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Sped_unidade(db.Model):
    __tablename__ = 'sped_unidade'
    codigo = Column(INTEGER, primary_key=True)
    unidade = Column(VARCHAR)
    descricao = Column(VARCHAR)
    fk_sped = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
