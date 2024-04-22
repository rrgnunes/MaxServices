from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Log_detalhe(Base):
    __tablename__ = 'log_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    log_master = Column(INTEGER)
    historico = Column(BLOB)
