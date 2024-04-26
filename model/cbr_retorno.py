from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Cbr_retorno(db.Model):
    __tablename__ = 'cbr_retorno'
    id_empresa = Column(INTEGER, primary_key=True)
    id_cbr_retorno = Column(BIGINT, primary_key=True)
    dthora_cadastro = Column(TIMESTAMP)
    dthora_processamento = Column(TIMESTAMP)
    dthora_arquivamento = Column(TIMESTAMP)
    arquivo = Column(BLOB)
    arquivo_nome = Column(VARCHAR)
    arquivo_data = Column(TIMESTAMP)
    arquivo_numero = Column(INTEGER)
    arquivo_local = Column(VARCHAR)
    arquivo_md5 = Column(VARCHAR)
    arquivo_quant_titulos = Column(INTEGER)
    situacao = Column(SMALLINT)
