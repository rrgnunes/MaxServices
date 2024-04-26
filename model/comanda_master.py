from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Comanda_master(db.Model):
    __tablename__ = 'comanda_master'
    codigo = Column(INTEGER, primary_key=True)
    fk_mesa = Column(INTEGER)
    total = Column(DECIMAL)
    situacao = Column(VARCHAR)
    data_hora = Column(TIMESTAMP)
