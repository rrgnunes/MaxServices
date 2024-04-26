from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Historico_sistema(db.Model):
    __tablename__ = 'historico_sistema'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    hora = Column(TIME)
    fk_usuario = Column(INTEGER)
    fk_tela = Column(INTEGER)
    operacao = Column(VARCHAR)
    historico = Column(BLOB)
    fk_empresa = Column(INTEGER)
