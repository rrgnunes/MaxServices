from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Os_master(db.Model):
    __tablename__ = 'os_master'
    codigo = Column(INTEGER, primary_key=True)
    data_inicio = Column(DATE)
    hora_inicio = Column(TIME)
    previsao_entrega = Column(DATE)
    data_termino = Column(DATE)
    hora_termino = Column(TIME)
    data_entrega = Column(DATE)
    hora_entrega = Column(TIME)
    fk_atendende = Column(INTEGER)
    problema = Column(BLOB)
    observacoes = Column(BLOB)
    fk_empresa = Column(INTEGER)
    fk_usuario = Column(INTEGER)
    documento = Column(VARCHAR)
    nome = Column(VARCHAR)
    fone1 = Column(VARCHAR)
    fone2 = Column(VARCHAR)
    situacao = Column(VARCHAR)
    numero_serie = Column(VARCHAR)
    descricao = Column(VARCHAR)
    modelo = Column(VARCHAR)
    marca = Column(VARCHAR)
    ano = Column(INTEGER)
    placa = Column(VARCHAR)
    km = Column(DECIMAL)
    subtotal = Column(DECIMAL)
    subtotal_pecas = Column(DECIMAL)
    subtotal_servicos = Column(DECIMAL)
    vl_desc_pecas = Column(DECIMAL)
    vl_desc_servicos = Column(DECIMAL)
    desc_perc_pecas = Column(DECIMAL)
    desc_perc_servicos = Column(DECIMAL)
    total_servicos = Column(DECIMAL)
    total_produtos = Column(DECIMAL)
    total_geral = Column(DECIMAL)
    endereco = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cidade = Column(VARCHAR)
    uf = Column(VARCHAR)
    data_emissao = Column(DATE)
    numero = Column(VARCHAR)
    nome_time = Column(VARCHAR)
    tipo_servico = Column(VARCHAR)
    fk_tipo_tecido = Column(INTEGER)
    quantidade = Column(INTEGER)
    fk_produto = Column(INTEGER)
    foto = Column(BLOB)
    fk_cliente = Column(INTEGER)
    descricao2 = Column(VARCHAR)
    faturado = Column(VARCHAR)