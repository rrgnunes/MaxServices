from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sped_config(Base):
    __tablename__ = 'sped_config'
    fk_empresa = Column(INTEGER, primary_key=True)
    ind_perfil = Column(VARCHAR)
    ind_ativ = Column(VARCHAR)
    ind_exp = Column(VARCHAR)
    ind_ccrf = Column(VARCHAR)
    ind_comb = Column(VARCHAR)
    ind_usina = Column(VARCHAR)
    ind_va = Column(VARCHAR)
    ind_ee = Column(VARCHAR)
    ind_cart = Column(VARCHAR)
    ind_form = Column(VARCHAR)
    ind_aer = Column(VARCHAR)
    cod_inc_trib = Column(VARCHAR)
    ind_apro_cred = Column(VARCHAR)
    cod_tipo_cont = Column(VARCHAR)
    cod_regime_tributario = Column(VARCHAR)
    ind_reg_cum = Column(VARCHAR)
    fk_usuario = Column(INTEGER)
    regime_tributario = Column(VARCHAR)
