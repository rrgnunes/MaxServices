from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cbr_retorno_titulos(db.Model):
    __tablename__ = 'cbr_retorno_titulos'
    id_empresa = Column(INTEGER, primary_key=True)
    id_cbr_retorno = Column(BIGINT, primary_key=True)
    id_cbr_retorno_titulos = Column(BIGINT, primary_key=True)
    titulo = Column(BIGINT)
    titulo_localizado = Column(CHAR)
    titulo_jaliquidado = Column(CHAR)
    titulo_semregistro = Column(CHAR)
    titulo_liquidado_limitep = Column(CHAR)
    titulo_recusado = Column(CHAR)
    seu_numero = Column(VARCHAR)
    nosso_numero = Column(VARCHAR)
    valor_documento = Column(NUMERIC)
    valor_pago = Column(NUMERIC)
    valor_recebido = Column(NUMERIC)
    valor_juros = Column(NUMERIC)
    valor_desconto = Column(NUMERIC)
    valor_despesa = Column(NUMERIC)
    data_ocorrencia = Column(DATE)
    id_banco = Column(VARCHAR)
    id_agencia = Column(VARCHAR)
    origem = Column(VARCHAR)
    forma_pagamento = Column(VARCHAR)
    tipo_ocorrencia = Column(INTEGER)
    tipo_ocorrencia_desc = Column(VARCHAR)
    mot_rej_comando = Column(VARCHAR)
    mot_rej_comando_desc = Column(VARCHAR)
    historico = Column(VARCHAR)
