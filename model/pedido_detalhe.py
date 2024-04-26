from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Pedido_detalhe(db.Model):
    __tablename__ = 'pedido_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fkpedido = Column(INTEGER)
    fkproduto = Column(INTEGER)
    quantidade = Column(DECIMAL)
    preco = Column(DECIMAL)
    total = Column(DECIMAL)
    vc = Column(DECIMAL)
    peso = Column(DECIMAL)
    frete = Column(DECIMAL)
    capacidade = Column(DECIMAL)
    produto = Column(VARCHAR)
    desconto_frete = Column(DECIMAL)
    total_liquido = Column(DECIMAL)
    comissao = Column(DECIMAL)
    total_comissao = Column(DECIMAL)
