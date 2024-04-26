from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Devolucao_master(db.Model):
    __tablename__ = 'devolucao_master'
    codigo = Column(INTEGER, primary_key=True)
    fk_venda = Column(INTEGER)
    fk_cliente = Column(INTEGER)
    data = Column(DATE)
    total = Column(DECIMAL)
    obs = Column(VARCHAR)
    situacao = Column(VARCHAR)
    fkempresa = Column(INTEGER)
    fk_vendedor = Column(INTEGER)
    tipo_devolucao = Column(VARCHAR)
