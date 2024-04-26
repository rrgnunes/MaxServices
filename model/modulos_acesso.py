from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Modulos_acesso(db.Model):
    __tablename__ = 'modulos_acesso'
    codigo = Column(INTEGER, primary_key=True)
    fk_usuario = Column(INTEGER)
    fk_modulo = Column(INTEGER)
    acesso = Column(VARCHAR)
