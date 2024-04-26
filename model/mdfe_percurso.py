from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Mdfe_percurso(db.Model):
    __tablename__ = 'mdfe_percurso'
    codigo = Column(INTEGER, primary_key=True)
    fk_mdfe_master = Column(INTEGER)
    uf = Column(VARCHAR)
