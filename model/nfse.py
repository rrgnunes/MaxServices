from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nfse(Base):
    __tablename__ = 'nfse'
    id_nfse = Column(INTEGER, primary_key=True)
    id_empresa = Column(INTEGER)
    id_numero = Column(INTEGER)
    id_serie = Column(INTEGER)
    dthr_emissao = Column(TIMESTAMP)
    id_pessoa = Column(INTEGER)
    id_situacao = Column(CHAR)
    xml_arquivo = Column(VARCHAR)
    xml_string = Column(BLOB)
    xml_protocolo = Column(VARCHAR)
    xml_protocolo_datahora = Column(TIMESTAMP)
    xml_string_protocolo = Column(BLOB)
    xml_canc_datahora = Column(TIMESTAMP)
    xml_canc_protocolo = Column(VARCHAR)
    xml_canc_string = Column(BLOB)
    ir = Column(DECIMAL)
    numero_lote = Column(VARCHAR)
    local_servico = Column(VARCHAR)
    envio_sincrono = Column(VARCHAR)
