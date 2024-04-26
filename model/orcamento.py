from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Orcamento(db.Model):
    __tablename__ = 'orcamento'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    fkvendedor = Column(INTEGER)
    fk_cliente = Column(INTEGER)
    cliente = Column(VARCHAR)
    telefone = Column(VARCHAR)
    celular = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cidade = Column(VARCHAR)
    uf = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    forma_pagamento = Column(VARCHAR)
    validade = Column(SMALLINT)
    obs = Column(BLOB)
    situacao = Column(VARCHAR)
    total = Column(DECIMAL)
    cep = Column(VARCHAR)
    fkempresa = Column(INTEGER)
    subtotal = Column(DECIMAL)
    percentual = Column(DECIMAL)
    desconto = Column(DECIMAL)
    codigo_web = Column(INTEGER)
    fk_fpg = Column(INTEGER)
    ncontrole = Column(INTEGER)
    fk_transp = Column(INTEGER)
    faturado = Column(VARCHAR)
