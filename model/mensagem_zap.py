from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mensagem_zap(Base):
    __tablename__ = 'mensagem_zap'
    codigo = Column(INTEGER, primary_key=True)
    data = Column(DATE)
    mensagem = Column(VARCHAR)
    anexo = Column(VARCHAR)
    fone = Column(VARCHAR)
    status = Column(VARCHAR)
    mensagem_padrao = Column(BLOB)
    nome = Column(VARCHAR)
    empresa = Column(VARCHAR)
    origem = Column(VARCHAR)
    hora = Column(TIME)
    caminho_anexo = Column(VARCHAR)
