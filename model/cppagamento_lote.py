from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cppagamento_lote(db.Model):
    __tablename__ = 'cppagamento_lote'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    fk_plano = Column(INTEGER)
    fk_fpg = Column(INTEGER)
    fk_conta = Column(INTEGER)
    saldo = Column(DECIMAL)
    juros_perc = Column(DECIMAL)
    juros_valor = Column(DECIMAL)
    total_c_juros = Column(DECIMAL)
    desconto_perc = Column(DECIMAL)
    desconto_valor = Column(DECIMAL)
    total_final = Column(DECIMAL)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    total_pago = Column(DECIMAL)
