from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pessoa_cobranca(Base):
    __tablename__ = 'pessoa_cobranca'
    fkcliente = Column(INTEGER, primary_key=True)
    endereco = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cidade = Column(VARCHAR)
    complemento = Column(VARCHAR)
    uf = Column(VARCHAR)
    cep = Column(VARCHAR)
    fone = Column(VARCHAR)
