from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Nfce_master(db.Model):
    __tablename__ = 'nfce_master'
    codigo = Column(INTEGER, primary_key=True)
    numero = Column(INTEGER)
    chave = Column(VARCHAR)
    modelo = Column(VARCHAR)
    serie = Column(VARCHAR)
    data_emissao = Column(DATE)
    data_saida = Column(DATE)
    hora_emissao = Column(TIME)
    hora_saida = Column(TIME)
    id_emitente = Column(INTEGER)
    id_cliente = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    fk_caixa = Column(INTEGER)
    fk_vendedor = Column(INTEGER)
    cpf_nota = Column(VARCHAR)
    subtotal = Column(DECIMAL)
    tipo_desconto = Column(VARCHAR)
    desconto = Column(DECIMAL)
    troco = Column(DECIMAL)
    dinheiro = Column(DECIMAL)
    total = Column(DECIMAL)
    baseicms = Column(DECIMAL)
    totalicms = Column(DECIMAL)
    baseicmspis = Column(DECIMAL)
    totalicmspis = Column(DECIMAL)
    baseicmscof = Column(DECIMAL)
    totalicmscofins = Column(DECIMAL)
    baseiss = Column(DECIMAL)
    totaliss = Column(DECIMAL)
    observacoes = Column(BLOB)
    situacao = Column(VARCHAR)
    email = Column(VARCHAR)
    xml = Column(BLOB)
    protocolo = Column(VARCHAR)
    motivocancelamento = Column(VARCHAR)
    trib_mun = Column(DECIMAL)
    trib_est = Column(DECIMAL)
    trib_fed = Column(DECIMAL)
    trib_imp = Column(DECIMAL)
    flag = Column(VARCHAR)
    aberto = Column(VARCHAR)
    fkempresa = Column(INTEGER)
    fk_venda = Column(INTEGER)
    outros = Column(DECIMAL)
    cnf = Column(VARCHAR)
    sat_numero_cfe = Column(INTEGER)
    sat_numero_serie = Column(VARCHAR)
    xml_cancelamento = Column(BLOB)
    totalicmsmonoret = Column(DECIMAL)
    totalqbcmonoret = Column(DECIMAL)
