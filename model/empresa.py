from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necess�rio
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Empresa(db.Model):
    __tablename__ = 'empresa'
    codigo = Column(INTEGER, primary_key=True)
    fantasia = Column(VARCHAR)
    razao = Column(VARCHAR)
    tipo = Column(VARCHAR)
    cnpj = Column(VARCHAR)
    ie = Column(VARCHAR)
    im = Column(VARCHAR)
    endereco = Column(VARCHAR)
    numero = Column(VARCHAR)
    complemento = Column(VARCHAR)
    bairro = Column(VARCHAR)
    cidade = Column(VARCHAR)
    uf = Column(VARCHAR)
    cep = Column(VARCHAR)
    fone = Column(VARCHAR)
    fax = Column(VARCHAR)
    site = Column(VARCHAR)
    logomarca = Column(BLOB)
    fundacao = Column(DATE)
    usu_cad = Column(SMALLINT)
    usu_atu = Column(SMALLINT)
    nserie = Column(VARCHAR)
    csenha = Column(VARCHAR)
    nterm = Column(VARCHAR)
    id_plano_transferencia_c = Column(INTEGER)
    id_plano_transferencia_d = Column(INTEGER)
    id_caixa_geral = Column(INTEGER)
    bloquear_estoque_negativo = Column(VARCHAR)
    id_cidade = Column(INTEGER)
    crt = Column(SMALLINT)
    id_uf = Column(SMALLINT)
    id_plano_venda = Column(INTEGER)
    obsfisco = Column(BLOB)
    cfop = Column(VARCHAR)
    csosn = Column(VARCHAR)
    cst_icms = Column(VARCHAR)
    aliq_icms = Column(DECIMAL)
    cst_entrada = Column(VARCHAR)
    cst_saida = Column(VARCHAR)
    aliq_pis = Column(DECIMAL)
    aliq_cof = Column(DECIMAL)
    cst_ipi = Column(VARCHAR)
    aliq_ipi = Column(DECIMAL)
    imp_f5 = Column(VARCHAR)
    imp_f6 = Column(VARCHAR)
    mostra_resumo_caixa = Column(VARCHAR)
    limite_diario = Column(DECIMAL)
    prazo_maximo = Column(SMALLINT)
    id_pla_conta_ficha_cli = Column(INTEGER)
    id_plano_conta_retirada = Column(INTEGER)
    usa_pdv = Column(VARCHAR)
    recibo_vias = Column(VARCHAR)
    id_plano_taxa_cartao = Column(INTEGER)
    obs_carne = Column(BLOB)
    caixa_unico = Column(VARCHAR)
    caixa_rapido = Column(VARCHAR)
    empresa_padrao = Column(SMALLINT)
    id_plano_conta_devolucao = Column(INTEGER)
    n_inicial_nfce = Column(INTEGER)
    n_inicial_nfe = Column(INTEGER)
    checa_estoque_fiscal = Column(VARCHAR)
    desconto_prod_promo = Column(VARCHAR)
    data_cadastro = Column(VARCHAR)
    data_validade = Column(VARCHAR)
    flag = Column(VARCHAR)
    lancar_cartao_credito = Column(VARCHAR)
    filtrar_empresa_login = Column(VARCHAR)
    enviar_email_nfe = Column(VARCHAR)
    transportadora = Column(VARCHAR)
    tabela_preco = Column(VARCHAR)
    taxa_venda_prazo = Column(DECIMAL)
    email_contador = Column(VARCHAR)
    autopecas = Column(VARCHAR)
    atualiza_pr_venda = Column(VARCHAR)
    informar_gtin = Column(VARCHAR)
    recolhe_fcp = Column(VARCHAR)
    difal_origem = Column(DECIMAL)
    difal_destino = Column(DECIMAL)
    exclui_pdv = Column(VARCHAR)
    venda_semente = Column(VARCHAR)
    checa = Column(VARCHAR)
    email = Column(VARCHAR)
    ultimonsu = Column(VARCHAR)
    ultimo_pedido = Column(INTEGER)
    tipo_contrato = Column(INTEGER)
    tipo_empresa = Column(INTEGER)
    qtd_mesas = Column(SMALLINT)
    bloquear_preco = Column(VARCHAR)
    exibe_resumo_caixa = Column(VARCHAR)
    id_plano_compra = Column(INTEGER)
    responsavel_tecnico = Column(VARCHAR)
    carencia_juros = Column(INTEGER)
    pesquisa_referencia = Column(VARCHAR)
    restaurante = Column(VARCHAR)
    exibe_f3 = Column(VARCHAR)
    exibe_f4 = Column(VARCHAR)
    ler_peso = Column(VARCHAR)
    tipo_juros = Column(VARCHAR)
    juros_dia = Column(DECIMAL)
    juros_mes = Column(DECIMAL)
    farmacia = Column(VARCHAR)
    checa_limite = Column(VARCHAR)
    emite_ecf = Column(VARCHAR)
    loja_roupa = Column(VARCHAR)
    desconto_maximo = Column(NUMERIC)
    chkmadereira = Column(SMALLINT)
    pagamento_dinheiro = Column(VARCHAR)
    responsavel_empresa = Column(VARCHAR)
    habilita_acrescimo = Column(VARCHAR)
    multi_idioma = Column(VARCHAR)
    codigo_pais = Column(INTEGER)
    cnae = Column(VARCHAR)
    obsnfce = Column(BLOB)
    cfop_externo = Column(VARCHAR)
    lancar_cartao_cr = Column(VARCHAR)
    usa_bluetooth_resta = Column(VARCHAR)
    puxa_cfop_produto = Column(VARCHAR)
    habilita_desconto_pdv = Column(VARCHAR)
    replicar_dados = Column(VARCHAR)
    id_plano_boleto = Column(INTEGER)
    segunda_via_nfce = Column(VARCHAR)
    csosn_externo = Column(VARCHAR)
    cst_externo = Column(VARCHAR)
    aliq_icms_externo = Column(DECIMAL)
    cod_fpg_dinheiro = Column(INTEGER)
    venda_combustivel = Column(VARCHAR)
    baixa_est_pdv = Column(VARCHAR)
    imprime_ficha = Column(VARCHAR)
    msg_garantia = Column(BLOB)
    obs_os = Column(BLOB)
    fechar_caixa_auto = Column(VARCHAR)
    caixa_boleto = Column(INTEGER)
    obscondicional = Column(VARCHAR)