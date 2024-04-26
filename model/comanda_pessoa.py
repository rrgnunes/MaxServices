from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Comanda_pessoa(db.Model):
    __tablename__ = 'comanda_pessoa'
    codigo = Column(INTEGER, primary_key=True)
    fk_comanda = Column(INTEGER)
    nome = Column(VARCHAR)
    situacao = Column(VARCHAR)
    total = Column(DECIMAL)
    total_rateio = Column(DECIMAL)
    flag = Column(VARCHAR)
    imprimiu = Column(VARCHAR)
    pdv = Column(VARCHAR)
    percentual = Column(DECIMAL)
