from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Pessoa_conta(db.Model):
    __tablename__ = 'pessoa_conta'
    codigo = Column(INTEGER, primary_key=True)
    fkpessoa = Column(INTEGER)
    data_emissao = Column(DATE)
    data_vencimento = Column(DATE)
    historico = Column(VARCHAR)
    entrada = Column(DECIMAL)
    saida = Column(DECIMAL)
    fkvenda = Column(INTEGER)
    fkempresa = Column(INTEGER)
    documento = Column(VARCHAR)
    fkplano = Column(INTEGER)
    bloqueado = Column(VARCHAR)
    fkpedido = Column(INTEGER)
    fk_fpg = Column(INTEGER)
    fk_conta = Column(INTEGER)
