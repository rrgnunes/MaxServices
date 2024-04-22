from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bandeiras(Base):
    __tablename__ = 'bandeiras'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    fk_operadora = Column(INTEGER)
    debito = Column(CHAR)
    credito = Column(CHAR)
    dias_recebimento = Column(INTEGER)
    dias_uteis = Column(CHAR)
