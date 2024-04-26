from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Sped_produtos(db.Model):
    __tablename__ = 'sped_produtos'
    codigo = Column(INTEGER, primary_key=True)
    fk_produto = Column(INTEGER)
    descricao = Column(VARCHAR)
    cod_barra = Column(VARCHAR)
    tipo_item = Column(VARCHAR)
    cod_ncm = Column(VARCHAR)
    aliq_icms = Column(NUMERIC)
    fk_unidade = Column(SMALLINT)
    fk_sped = Column(INTEGER)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
