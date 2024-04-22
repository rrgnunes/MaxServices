from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sincronizar(Base):
    __tablename__ = 'sincronizar'
    codigo = Column(INTEGER, primary_key=True)
    servidor = Column(VARCHAR)
    nome = Column(VARCHAR)
    senha = Column(VARCHAR)
    usuario = Column(VARCHAR)
    banco = Column(VARCHAR)
    path = Column(VARCHAR)
    envia = Column(VARCHAR)
    recebe = Column(VARCHAR)
    tempo = Column(INTEGER)
    porta = Column(VARCHAR)
    limite = Column(INTEGER)
    driver = Column(VARCHAR)
    prioridade = Column(INTEGER)
