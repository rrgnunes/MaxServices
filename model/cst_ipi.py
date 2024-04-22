from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cst_ipi(Base):
    __tablename__ = 'cst_ipi'
    codigo = Column(VARCHAR, primary_key=True)
    descricao = Column(VARCHAR)
    tipo = Column(VARCHAR)
