from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Telas(db.Model):
    __tablename__ = 'telas'
    codigo = Column(INTEGER, primary_key=True)
    tela = Column(VARCHAR)
    nivel = Column(SMALLINT)
    pai = Column(SMALLINT)
    nome = Column(VARCHAR)
    flag = Column(VARCHAR)
