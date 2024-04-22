from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Unidade(Base):
    __tablename__ = 'unidade'
    codigo = Column(VARCHAR, primary_key=True)
    descricao = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
