from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sped_h005(Base):
    __tablename__ = 'sped_h005'
    codigo = Column(INTEGER, primary_key=True)
    dt_inv = Column(DATE)
    vl_inv = Column(NUMERIC)
    fk_sped = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
