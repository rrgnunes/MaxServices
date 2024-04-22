from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mdfe_detalhe(Base):
    __tablename__ = 'mdfe_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fk_mdfe_master = Column(INTEGER)
    chave = Column(VARCHAR)
    valor = Column(DECIMAL)
    peso = Column(DECIMAL)
    numero = Column(INTEGER)
    fk_destinatario = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
