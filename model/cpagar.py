from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cpagar(Base):
    __tablename__ = 'cpagar'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    fkfornece = Column(INTEGER)
    doc = Column(VARCHAR)
    valor = Column(DECIMAL)
    dtvencimento = Column(DATE)
    historico = Column(VARCHAR)
    data_pagamento = Column(DATE)
    desconto = Column(DECIMAL)
    juros = Column(DECIMAL)
    vlpago = Column(DECIMAL)
    vl_restante = Column(DECIMAL)
    situacao = Column(VARCHAR)
    fkempresa = Column(INTEGER)
    fk_compra = Column(INTEGER)
    fk_fpg = Column(INTEGER)
    flag = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
