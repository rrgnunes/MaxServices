from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cbr_remessa_titulos(db.Model):
    __tablename__ = 'cbr_remessa_titulos'
    id_empresa = Column(INTEGER, primary_key=True)
    id_cbr_remessa = Column(BIGINT, primary_key=True)
    id_cbr_titulos = Column(BIGINT, primary_key=True)
    dt_emissao = Column(TIMESTAMP)
    dt_vencimento = Column(TIMESTAMP)
    valor = Column(NUMERIC)
    cli_razaosocial = Column(VARCHAR)
    cli_cnpjcpf = Column(VARCHAR)
    cli_endereco = Column(VARCHAR)
    cli_endnumero = Column(VARCHAR)
    cli_endbairro = Column(VARCHAR)
    cli_endcidade = Column(VARCHAR)
    cli_enduf = Column(CHAR)
    cli_endcep = Column(VARCHAR)
    dt_pagamento = Column(DATE)
    cancelamento_loja = Column(CHAR)
    pagamento_loja = Column(CHAR)
    alteracao_loja = Column(CHAR)
