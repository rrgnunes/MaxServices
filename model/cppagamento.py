from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cppagamento(db.Model):
    __tablename__ = 'cppagamento'
    codigo = Column(INTEGER, primary_key=True)
    fkpagar = Column(INTEGER)
    data = Column(DATE)
    valor_parcela = Column(DECIMAL)
    perc_juros = Column(DECIMAL)
    juros = Column(DECIMAL)
    perc_desconto = Column(DECIMAL)
    desconto = Column(DECIMAL)
    valor_recebido = Column(DECIMAL)
    fkplano = Column(INTEGER)
    fkusuario = Column(INTEGER)
    fkkempresa = Column(INTEGER)
    fkconta = Column(INTEGER)
    fk_forma_pgto = Column(INTEGER)
    numero_cheque = Column(INTEGER)
    fkfornecedor = Column(INTEGER)
    fk_lote = Column(INTEGER)
