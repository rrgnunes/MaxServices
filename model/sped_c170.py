from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Sped_c170(db.Model):
    __tablename__ = 'sped_c170'
    codigo = Column(INTEGER, primary_key=True)
    descricao = Column(VARCHAR)
    qtd = Column(NUMERIC)
    vl_item = Column(NUMERIC)
    vl_desc = Column(NUMERIC)
    ind_mov = Column(VARCHAR)
    cfop = Column(VARCHAR)
    cst_icms = Column(VARCHAR)
    cod_nat = Column(VARCHAR)
    vl_bc_icms = Column(NUMERIC)
    aliq_icm = Column(NUMERIC)
    vl_icms = Column(NUMERIC)
    vl_bc_icms_st = Column(NUMERIC)
    aliq_st = Column(NUMERIC)
    vl_icms_st = Column(NUMERIC)
    ind_apur = Column(VARCHAR)
    cst_ipi = Column(VARCHAR)
    cod_enq = Column(VARCHAR)
    vl_bc_ipi = Column(NUMERIC)
    aliq_ipi = Column(NUMERIC)
    vl_ipi = Column(NUMERIC)
    cst_pis = Column(VARCHAR)
    vl_bc_pis = Column(NUMERIC)
    aliq_pis_perc = Column(NUMERIC)
    quant_bc_pis = Column(NUMERIC)
    aliq_pis_r = Column(NUMERIC)
    vl_pis = Column(NUMERIC)
    cst_cofins = Column(VARCHAR)
    vl_bc_cofins = Column(NUMERIC)
    aliq_cofins_perc = Column(NUMERIC)
    quant_bc_cofins = Column(NUMERIC)
    aliq_cofins_r = Column(NUMERIC)
    vl_cofins = Column(NUMERIC)
    cod_cta = Column(VARCHAR)
    vl_opr = Column(NUMERIC)
    fk_produto = Column(INTEGER)
    fk_unidade = Column(INTEGER)
    fk_c100 = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
