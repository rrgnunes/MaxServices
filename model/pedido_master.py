from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Pedido_master(db.Model):
    __tablename__ = 'pedido_master'
    codigo = Column(INTEGER, primary_key=True)
    fkempresa = Column(INTEGER)
    fkcliente = Column(INTEGER)
    endereco_cobranca = Column(VARCHAR)
    complemento_cobranca = Column(VARCHAR)
    bairro_cobranca = Column(VARCHAR)
    cidade_cobranca = Column(VARCHAR)
    uf_cobranca = Column(VARCHAR)
    cep_cobranca = Column(VARCHAR)
    fone_cobranca = Column(VARCHAR)
    endereco_entrega = Column(VARCHAR)
    complemento_entrega = Column(VARCHAR)
    bairro_entrega = Column(VARCHAR)
    cidade_entrega = Column(VARCHAR)
    uf_entrega = Column(VARCHAR)
    cep_entrega = Column(VARCHAR)
    tipo_frete = Column(VARCHAR)
    condicoes_pagamento = Column(BLOB)
    obs = Column(BLOB)
    total = Column(DECIMAL)
    propriedade = Column(VARCHAR)
    banco = Column(VARCHAR)
    agencia = Column(VARCHAR)
    gerente = Column(VARCHAR)
    fone_banco = Column(VARCHAR)
    tipo = Column(VARCHAR)
    situacao = Column(VARCHAR)
    forma_entrega = Column(VARCHAR)
    representante = Column(VARCHAR)
    condicao_pagamento = Column(VARCHAR)
    forma_pagamento = Column(VARCHAR)
    data = Column(DATE)
    numero = Column(INTEGER)
    prazo_entrega = Column(VARCHAR)
    cliente_nome = Column(VARCHAR)
    cliente_fone = Column(VARCHAR)
    cliente_uf = Column(VARCHAR)
    cliente_cnpj = Column(VARCHAR)
    cliente_ie = Column(VARCHAR)
    cliente_cidade = Column(VARCHAR)
    total_frete = Column(DECIMAL)
    total_liquido = Column(DECIMAL)
    fk_fornecedor = Column(INTEGER)
    gera_financeiro = Column(VARCHAR)
    total_comissao = Column(DECIMAL)
