from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contas_movimento(Base):
    __tablename__ = 'contas_movimento'
    codigo = Column(INTEGER, primary_key=True)
    id_conta_caixa = Column(INTEGER)
    id_usuario = Column(INTEGER)
    historico = Column(VARCHAR)
    data = Column(DATE)
    hora = Column(TIME)
    entrada = Column(DECIMAL)
    saida = Column(DECIMAL)
    fkvenda = Column(INTEGER)
    lote = Column(INTEGER)
    troca = Column(DECIMAL)
    saldo = Column(BIGINT)
    troco = Column(DECIMAL)
