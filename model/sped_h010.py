from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Sped_h010(db.Model):
    __tablename__ = 'sped_h010'
    codigo = Column(INTEGER, primary_key=True)
    qtd = Column(NUMERIC)
    vl_unit = Column(NUMERIC)
    vl_item = Column(NUMERIC)
    ind_prop = Column(VARCHAR)
    cod_part = Column(INTEGER)
    txt_compl = Column(VARCHAR)
    cod_cta = Column(VARCHAR)
    fk_h005 = Column(INTEGER)
    fk_produto = Column(INTEGER)
    fk_unidade = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
