from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Log_master(Base):
    __tablename__ = 'log_master'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    hora = Column(TIME)
    fk_usuario = Column(INTEGER)
    tela = Column(VARCHAR)
    operacao = Column(VARCHAR)
    fk_empresa = Column(INTEGER)
    descricao = Column(VARCHAR)
    registro = Column(VARCHAR)
