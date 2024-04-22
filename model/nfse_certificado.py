from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nfse_certificado(Base):
    __tablename__ = 'nfse_certificado'
    id_empresa = Column(INTEGER, primary_key=True)
    id_modelo = Column(INTEGER, primary_key=True)
    id_certificadoconfig = Column(INTEGER, primary_key=True)
    certificado_numero = Column(VARCHAR)
    certificado_senha = Column(VARCHAR)
    ws_uf_destino = Column(CHAR)
    ws_timeout = Column(INTEGER)
    id_tipo_ambiente = Column(INTEGER)
    id_ssl_type = Column(INTEGER)
    id_crypt_type = Column(INTEGER)
    id_http_type = Column(INTEGER)
    id_xmlsign_type = Column(INTEGER)
    ws_proxy_host = Column(VARCHAR)
    ws_proxy_porta = Column(INTEGER)
    ws_proxy_usuario = Column(VARCHAR)
    ws_proxy_senha = Column(VARCHAR)
    id_report_orientacao = Column(INTEGER)
    id_forma_emissao = Column(INTEGER)
    email_enviar = Column(CHAR)
    email_servidor = Column(VARCHAR)
    email_porta = Column(INTEGER)
    email_usuario = Column(VARCHAR)
    email_senha = Column(VARCHAR)
    email_senha_segura = Column(CHAR)
    time_zone_modo = Column(INTEGER)
    time_zone_manual = Column(INTEGER)
    manter_arquivos_temporarios = Column(CHAR)
    logomarca = Column(VARCHAR)
    campos_fat_obrigatorio = Column(CHAR)
    nfse_soap_salvar_envelope = Column(CHAR)
    nfse_path_schemas = Column(VARCHAR)
    nfse_web_user = Column(VARCHAR)
    nfse_web_pwd = Column(VARCHAR)
    nfse_logo_prf = Column(VARCHAR)
    envio_sincrono = Column(VARCHAR)
    serie = Column(VARCHAR)
