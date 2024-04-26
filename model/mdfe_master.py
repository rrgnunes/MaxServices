from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Mdfe_master(db.Model):
    __tablename__ = 'mdfe_master'
    codigo = Column(INTEGER, primary_key=True)
    fk_transportador = Column(INTEGER)
    numero_mdfe = Column(INTEGER)
    data = Column(DATE)
    id_municipio = Column(VARCHAR)
    uf_inicio = Column(VARCHAR)
    uf_fim = Column(VARCHAR)
    qtd_cte = Column(INTEGER)
    valor_carga = Column(DECIMAL)
    unidade_carga = Column(VARCHAR)
    qtd_carga = Column(DECIMAL)
    fk_empresa = Column(SMALLINT)
    infcpl = Column(BLOB)
    infadfisco = Column(BLOB)
    chave = Column(VARCHAR)
    protocolo = Column(VARCHAR)
    xml = Column(BLOB)
    data_emissao = Column(DATE)
    situacao = Column(VARCHAR)
    resp_seguro = Column(SMALLINT)
    tipo_mdfe = Column(VARCHAR)
    tipo = Column(VARCHAR)
    nome_seguradora = Column(VARCHAR)
    cpf_seguradora = Column(VARCHAR)
    numero_apolice = Column(VARCHAR)
    placa = Column(VARCHAR)
    id_origem = Column(INTEGER)
    id_destino = Column(INTEGER)
    carga_propria = Column(VARCHAR)
    cnpj_responsavel = Column(VARCHAR)
    numero_averbacao = Column(VARCHAR)
    serie = Column(INTEGER)
