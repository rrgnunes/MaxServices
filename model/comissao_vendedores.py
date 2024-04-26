from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Comissao_vendedores(db.Model):
    __tablename__ = 'comissao_vendedores'
    codigo = Column(INTEGER, primary_key=True)
    fk_empresa = Column(INTEGER)
    fk_vendedor = Column(INTEGER)
    fk_vendafpg = Column(INTEGER)
    fk_fpg = Column(INTEGER)
    data_lancamento = Column(DATE)
    valor = Column(DECIMAL)
