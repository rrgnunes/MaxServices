from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Responsavel_tecnico(Base):
    __tablename__ = 'responsavel_tecnico'
    codigo = Column(INTEGER, primary_key=True)
    cnpj = Column(VARCHAR)
    nome = Column(VARCHAR)
    email = Column(VARCHAR)
    telefone = Column(VARCHAR)
    idcsrt = Column(VARCHAR)
    csrt = Column(VARCHAR)
