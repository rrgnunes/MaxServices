from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Xml_master(Base):
    __tablename__ = 'xml_master'
    codigo = Column(INTEGER, primary_key=True)
    id_fornecedor = Column(INTEGER)
    data_pedido = Column(DATE)
    data_entrada = Column(DATE)
    data_emissao_nf = Column(DATE)
    nota_fiscal = Column(VARCHAR)
    sub_total = Column(DECIMAL)
    frete = Column(DECIMAL)
    outras_despesas = Column(DECIMAL)
    seguro = Column(DECIMAL)
    desconto = Column(DECIMAL)
    total = Column(DECIMAL)
    modelo = Column(VARCHAR)
    serie = Column(VARCHAR)
    chave = Column(VARCHAR)
    cfop = Column(VARCHAR)
    base_pis = Column(DECIMAL)
    total_pis = Column(DECIMAL)
    base_cofins = Column(DECIMAL)
    total_cofins = Column(DECIMAL)
    base_ipi = Column(DECIMAL)
    total_ipi = Column(DECIMAL)
    base_icms = Column(DECIMAL)
    total_icms = Column(DECIMAL)
    base_st = Column(DECIMAL)
    total_st = Column(DECIMAL)
    empresa = Column(INTEGER)
    xml = Column(BLOB)
    fk_usuario = Column(INTEGER)
