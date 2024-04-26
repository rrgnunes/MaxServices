from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Caixa(db.Model):
    __tablename__ = 'caixa'
    codigo = Column(INTEGER, primary_key=True)
    emissao = Column(DATE)
    doc = Column(VARCHAR)
    fkplano = Column(INTEGER)
    fkconta = Column(INTEGER)
    historico = Column(VARCHAR)
    entrada = Column(NUMERIC)
    saida = Column(NUMERIC)
    saldo = Column(NUMERIC)
    fkvenda = Column(INTEGER)
    fkcompra = Column(INTEGER)
    fkpagar = Column(INTEGER)
    fkreceber = Column(INTEGER)
    transferencia = Column(INTEGER)
    bloqueado = Column(VARCHAR)
    fk_conta1 = Column(INTEGER)
    fk_pai = Column(INTEGER)
    hora_emissao = Column(TIME)
    ecartao = Column(VARCHAR)
    id_usuario = Column(INTEGER)
    empresa = Column(INTEGER)
    fk_ficha_cli = Column(INTEGER)
    visivel = Column(VARCHAR)
    dt_cadastro = Column(DATE)
    fk_devolucao = Column(INTEGER)
    fk_cartao = Column(INTEGER)
    tipo_movimento = Column(VARCHAR)
    id_subcaixa = Column(INTEGER)
    fpg = Column(INTEGER)
    fk_os = Column(INTEGER)
