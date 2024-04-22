from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Agenda(Base):
    __tablename__ = 'agenda'
    codigo = Column(INTEGER, primary_key=True)
    cliente = Column(INTEGER)
    atendente = Column(INTEGER)
    servico = Column(INTEGER)
    status = Column(INTEGER)
    duracao = Column(INTEGER)
    data = Column(TIMESTAMP)
    horario = Column(TIMESTAMP)
    fim = Column(TIMESTAMP)
    descricao_cliente = Column(VARCHAR)
    telefone1 = Column(VARCHAR)
    telefone2 = Column(VARCHAR)
    descricao_servico = Column(VARCHAR)
    observacao = Column(VARCHAR)
