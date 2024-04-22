from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cbr_remessa(Base):
    __tablename__ = 'cbr_remessa'
    id_empresa = Column(INTEGER, primary_key=True)
    id_cbr_remessa = Column(BIGINT, primary_key=True)
    id_cbr_remessa_uuid = Column(VARCHAR)
    data = Column(TIMESTAMP)
    idbanco = Column(SMALLINT)
    agencia = Column(VARCHAR)
    agencia_digito = Column(CHAR)
    conta = Column(VARCHAR)
    conta_digito = Column(CHAR)
    codigo_cedente = Column(VARCHAR)
    convenio = Column(VARCHAR)
    modalidade = Column(CHAR)
    local_de_pagamento = Column(VARCHAR)
    mensagem = Column(VARCHAR)
    instrucao1 = Column(VARCHAR)
    instrucao2 = Column(VARCHAR)
    percentual_juros = Column(NUMERIC)
    percentual_multa = Column(NUMERIC)
    carteira = Column(VARCHAR)
    arquivo = Column(BLOB)
    data_geracao = Column(TIMESTAMP)
    local_arquivo = Column(VARCHAR)
    data_proc_banco = Column(TIMESTAMP)
    cancelada = Column(CHAR)
    dig_cedente = Column(VARCHAR)
