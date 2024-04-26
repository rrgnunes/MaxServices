from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfce_detalhe(db.Model):
    __tablename__ = 'nfce_detalhe'
    codigo = Column(INTEGER, primary_key=True)
    fkvenda = Column(INTEGER)
    id_produto = Column(INTEGER)
    item = Column(SMALLINT)
    cod_barra = Column(VARCHAR)
    ncm = Column(VARCHAR)
    cfop = Column(VARCHAR)
    cst = Column(VARCHAR)
    csosn = Column(VARCHAR)
    tipo = Column(VARCHAR)
    qtd = Column(DECIMAL)
    e_medio = Column(DECIMAL)
    preco = Column(DECIMAL)
    valor_item = Column(DECIMAL)
    vdesconto = Column(DECIMAL)
    base_icms = Column(DECIMAL)
    aliq_icms = Column(DECIMAL)
    valor_icms = Column(DECIMAL)
    p_reducao_icms = Column(DECIMAL)
    cst_cofins = Column(VARCHAR)
    base_cofins_icms = Column(DECIMAL)
    aliq_cofins_icms = Column(DECIMAL)
    valor_cofins_icms = Column(DECIMAL)
    cst_pis = Column(VARCHAR)
    base_pis_icms = Column(DECIMAL)
    aliq_pis_icms = Column(DECIMAL)
    valor_pis_icms = Column(DECIMAL)
    base_iss = Column(DECIMAL)
    aliq_iss = Column(DECIMAL)
    valor_iss = Column(DECIMAL)
    cmunfg = Column(INTEGER)
    clistaserv = Column(INTEGER)
    trib_mun = Column(DECIMAL)
    trib_est = Column(DECIMAL)
    trib_fed = Column(DECIMAL)
    trib_imp = Column(DECIMAL)
    situacao = Column(VARCHAR)
    flag = Column(VARCHAR)
    unidade = Column(VARCHAR)
    total = Column(BIGINT)
    outros = Column(DECIMAL)
    cest = Column(VARCHAR)
    vicmsmonoret = Column(DECIMAL)
    qbcmomoret = Column(DECIMAL)
