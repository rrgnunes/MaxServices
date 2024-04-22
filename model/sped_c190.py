from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sped_c190(Base):
    __tablename__ = 'sped_c190'
    codigo = Column(INTEGER, primary_key=True)
    cst_icms = Column(VARCHAR)
    aliq_icms = Column(NUMERIC)
    vl_opr = Column(NUMERIC)
    vl_bc_icms = Column(NUMERIC)
    vl_icms = Column(NUMERIC)
    vl_bc_icms_st = Column(NUMERIC)
    vl_icms_st = Column(NUMERIC)
    vl_red_bc = Column(NUMERIC)
    vl_ipi = Column(NUMERIC)
    cod_obs = Column(VARCHAR)
    cfop = Column(VARCHAR)
    fk_c100 = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
